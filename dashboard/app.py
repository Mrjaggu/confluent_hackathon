import streamlit as st
from confluent_kafka import Consumer, Producer
import json
import time
from datetime import datetime
import uuid

def read_config():
    """Read Kafka configuration from client.properties file"""
    config = {}
    try:
        with open("client.properties") as fh:
            for line in fh:
                if "=" in line and not line.startswith("#"):
                    key, val = line.strip().split("=", 1)
                    config[key] = val
    except FileNotFoundError:
        st.error("❌ client.properties file not found!")
        return None
    return config

def create_producer():
    """Create and configure Kafka producer"""
    config = read_config()
    if config is None:
        return None
    
    try:
        producer = Producer(config)
        return producer
    except Exception as e:
        st.error(f"❌ Failed to create producer: {str(e)}")
        return None

def create_consumer():
    """Create and configure Kafka consumer"""
    config = read_config()
    if config is None:
        return None
    
    config["group.id"] = "streamlit-consumer"
    config["auto.offset.reset"] = "earliest"
    config["enable.auto.commit"] = "true"
    
    try:
        consumer = Consumer(config)
        consumer.subscribe(["movie_insights"])
        return consumer
    except Exception as e:
        st.error(f"❌ Failed to create consumer: {str(e)}")
        return None

def producer_page():
    """Producer page for sending movie queries"""
    st.title("🎬 Movie Recommendation")
    st.subheader("Send Movie Recommendation Queries")
    
    # Initialize producer
    if 'producer' not in st.session_state:
        st.session_state.producer = create_producer()
    
    if st.session_state.producer is None:
        st.error("Cannot create producer. Check your configuration.")
        return
    
    # Form for movie query
    with st.form("movie_query_form"):
        st.write("### 📝 Create Movie Query")
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input(
                "User ID", 
                value=f"U{len(st.session_state.get('sent_queries', []))+1}",
                help="Unique identifier for the user"
            )
        
        with col2:
            query_type = st.selectbox(
                "Query Type",
                ["recommendation", "search", "similar", "genre"],
                help="Type of movie query"
            )
        
        prompt = st.text_area(
            "Movie Prompt", 
            placeholder="e.g., Recommend a movie like 'Inception' or 'Show me action movies from 2020'",
            help="Describe what kind of movie recommendation you want"
        )
        
        # Additional parameters
        with st.expander("🔧 Advanced Options", expanded=False):
            genre = st.selectbox(
                "Preferred Genre (optional)",
                ["", "action", "comedy", "drama", "horror", "romance", "sci-fi", "thriller"],
                help="Filter by specific genre"
            )
            
            year_range = st.slider(
                "Year Range (optional)",
                min_value=1900,
                max_value=2024,
                value=(2000, 2024),
                help="Filter movies by release year"
            )
            
            rating_min = st.slider(
                "Minimum Rating",
                min_value=0.0,
                max_value=10.0,
                value=6.0,
                step=0.1,
                help="Minimum IMDB rating"
            )
        
        submitted = st.form_submit_button("🚀 Send Query", use_container_width=True)
        
        if submitted:
            if not user_id.strip():
                st.error("❌ User ID is required!")
            elif not prompt.strip():
                st.error("❌ Movie prompt is required!")
            else:
                # Create query object
                query = {
                    "query_id": str(uuid.uuid4()),
                    "user_id": user_id.strip(),
                    "type": query_type,
                    "prompt": prompt.strip(),
                    "timestamp": datetime.now().isoformat(),
                    "parameters": {
                        "genre": genre if genre else None,
                        "year_range": year_range,
                        "min_rating": rating_min
                    }
                }
                
                try:
                    # Send to Kafka
                    st.session_state.producer.produce(
                        "movie_queries", 
                        value=json.dumps(query).encode("utf-8")
                    )
                    st.session_state.producer.flush()
                    
                    # Store in session state for history
                    if 'sent_queries' not in st.session_state:
                        st.session_state.sent_queries = []
                    st.session_state.sent_queries.append(query)
                    
                    st.success(f"✅ Query sent successfully! Query ID: {query['query_id']}")
                    
                except Exception as e:
                    st.error(f"❌ Failed to send query: {str(e)}")
    
    # Display sent queries history
    st.subheader("📋 Query History")
    
    if 'sent_queries' in st.session_state and st.session_state.sent_queries:
        for i, query in enumerate(reversed(st.session_state.sent_queries)):
            with st.expander(f"Query #{len(st.session_state.sent_queries)-i} - {query['user_id']} ({query['type']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**User ID:** {query['user_id']}")
                    st.write(f"**Type:** {query['type']}")
                    st.write(f"**Timestamp:** {query['timestamp']}")
                with col2:
                    st.write(f"**Query ID:** {query['query_id']}")
                    if query['parameters']['genre']:
                        st.write(f"**Genre:** {query['parameters']['genre']}")
                    st.write(f"**Min Rating:** {query['parameters']['min_rating']}")
                
                st.write(f"**Prompt:** {query['prompt']}")
                
                if st.button(f"🔄 Resend Query", key=f"resend_{query['query_id']}"):
                    try:
                        # Create new query with updated timestamp
                        new_query = query.copy()
                        new_query['query_id'] = str(uuid.uuid4())
                        new_query['timestamp'] = datetime.now().isoformat()
                        
                        st.session_state.producer.produce(
                            "movie_queries", 
                            value=json.dumps(new_query).encode("utf-8")
                        )
                        st.session_state.producer.flush()
                        st.success("✅ Query resent successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to resend query: {str(e)}")
    else:
        st.info("No queries sent yet. Use the form above to send your first movie query!")
    
    # Clear history button
    if st.button("🗑️ Clear History"):
        st.session_state.sent_queries = []
        st.success("History cleared!")
        st.rerun()

def consumer_page():
    """Consumer page for viewing movie insights"""
    st.title("🔍 Movie Insights Consumer")
    st.subheader("Real-time Movie Recommendations")
    
    # Initialize session state
    if 'consuming' not in st.session_state:
        st.session_state.consuming = False
    if 'consumer' not in st.session_state:
        st.session_state.consumer = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'message_count' not in st.session_state:
        st.session_state.message_count = 0
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🚀 Start Consuming", disabled=st.session_state.consuming):
            if st.session_state.consumer is None:
                st.session_state.consumer = create_consumer()
            
            if st.session_state.consumer is not None:
                st.session_state.consuming = True
                st.session_state.messages = []
                st.session_state.message_count = 0
                st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Consuming", disabled=not st.session_state.consuming):
            st.session_state.consuming = False
            if st.session_state.consumer:
                st.session_state.consumer.close()
                st.session_state.consumer = None
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Messages"):
            st.session_state.messages = []
            st.session_state.message_count = 0
            st.rerun()
    
    # Status display
    if st.session_state.consuming:
        status_placeholder = st.empty()
        
        if st.session_state.consumer:
            try:
                msg = st.session_state.consumer.poll(0.1)
                
                if msg is not None and not msg.error():
                    message_data = json.loads(msg.value().decode("utf-8"))
                    st.session_state.message_count += 1
                    
                    message_entry = {
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'count': st.session_state.message_count,
                        'data': message_data
                    }
                    st.session_state.messages.append(message_entry)
                    
                    if len(st.session_state.messages) > 50:
                        st.session_state.messages = st.session_state.messages[-50:]
                    
                    status_placeholder.success(f"✅ Connected - {st.session_state.message_count} messages received | Latest: {json.dumps(message_data)[:100]}{'...' if len(json.dumps(message_data)) > 100 else ''}")
                else:
                    status_placeholder.info(f"⏳ Waiting for messages... ({st.session_state.message_count} received)")
                    
            except Exception as e:
                st.error(f"❌ Error polling messages: {str(e)}")
                st.session_state.consuming = False
        
        time.sleep(1)
        st.rerun()
    else:
        st.info("🔴 Consumer stopped - Click 'Start Consuming' to begin")
    
    # Messages display
    st.subheader(f"📨 Movie Insights ({len(st.session_state.messages)} displayed)")
    
    if st.session_state.messages:
        for message in reversed(st.session_state.messages):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Message #{message['count']}**")
                with col2:
                    st.write(f"🕒 {message['timestamp']}")
                
                with st.expander("📄 Raw Message", expanded=False):
                    st.code(json.dumps(message['data'], indent=2), language='json')
                
                st.write("**📋 Movie Insight:**")
                
                if isinstance(message['data'], dict):
                    for key, value in message['data'].items():
                        if isinstance(value, (dict, list)):
                            st.write(f"**{key}:**")
                            st.json(value)
                        else:
                            st.write(f"**{key}:** {value}")
                else:
                    st.json(message['data'])
                
                st.caption(f"Insight received at {message['timestamp']} (Message #{message['count']})")
                st.divider()
    else:
        st.info("No insights received yet. Start consuming to see movie recommendations appear here.")

def main():
    st.set_page_config(
        page_title="Kafka Movie App",
        page_icon="🎬",
        layout="wide"
    )
    
    # Sidebar for navigation
    with st.sidebar:
        st.title("🎬 Agentic Ai Movie recommender App")
        page = st.radio(
            "Navigate to:",
            ["🚀 Send Queries", "📨 View Insights"],
            help="Choose between sending movie queries or viewing real-time insights"
        )
        
        st.divider()
        
        # Configuration info
        st.header("⚙️ Configuration")
        st.write("**Query Topic:** movie_queries")
        st.write("**Insights Topic:** movie_insights")
        st.write("**Consumer Group:** streamlit-consumer")
        
        # Stats
        if 'sent_queries' in st.session_state:
            st.write(f"**Queries Sent:** {len(st.session_state.sent_queries)}")
        if 'message_count' in st.session_state:
            st.write(f"**Insights Received:** {st.session_state.message_count}")
    
    # Route to appropriate page
    if page == "🚀 Send Queries":
        producer_page()
    else:
        consumer_page()

if __name__ == "__main__":
    main()