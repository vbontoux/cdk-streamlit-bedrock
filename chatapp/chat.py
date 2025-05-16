import boto3
import streamlit as st
import json
import uuid
import time
from botocore.exceptions import ClientError, NoCredentialsError

# Track app runs for debugging
st.session_state["i"] = 0 if "i" not in st.session_state else st.session_state["i"] + 1
print("Run #", st.session_state["i"])

def get_aliases(agent_client, agent):
    """Get aliases for the selected agent with error handling"""
    aliases = [("-", "-")]
    if agent and agent[0] != "-":
        try:
            response = agent_client.list_agent_aliases(
                agentId=agent[1],
                maxResults=123
            )
            aliases = [(a["agentAliasName"], a["agentAliasId"]) for a in response["agentAliasSummaries"]]
            if not aliases:  # If no aliases found, return default
                aliases = [("-", "-")]
        except (ClientError, NoCredentialsError) as e:
            st.sidebar.error(f"Error fetching aliases: {str(e)}")
            print(f"Error fetching aliases: {str(e)}")
    return aliases

def initialize_boto_clients():
    """Initialize boto3 clients with error handling"""
    try:
        agent_client = boto3.client('bedrock-agent')
        agent_runtime_client = boto3.client('bedrock-agent-runtime')
        return agent_client, agent_runtime_client, None
    except (ClientError, NoCredentialsError) as e:
        error_msg = f"Failed to initialize AWS clients: {str(e)}"
        print(error_msg)
        return None, None, error_msg

def get_session_id():
    """Generate or retrieve a session ID for the conversation"""
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    return st.session_state["session_id"]

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by Bedrock agents")

# Initialize AWS clients
agent_client, agent_runtime_client, client_error = initialize_boto_clients()

# Display error if client initialization failed
if client_error:
    st.error(client_error)
    st.stop()

# Initialize agents list
agents = [("-", "-")]
if "agents" not in st.session_state:
    try:
        agts = agent_client.list_agents(maxResults=123)
        print("AGTS =>", agts)
        if agts.get("agentSummaries"):
            st.session_state["agents"] = [(a["agentName"], a["agentId"]) for a in agts["agentSummaries"]]
        else:
            st.session_state["agents"] = [("-", "-")]
    except (ClientError, NoCredentialsError) as e:
        st.error(f"Error listing agents: {str(e)}")
        print(f"Error listing agents: {str(e)}")
        st.session_state["agents"] = [("-", "-")]

print("AGENTS =>", st.session_state["agents"])
agents = st.session_state["agents"]
agent = None

# Sidebar for agent selection
with st.sidebar:
    agent = st.selectbox("Agents", options=[(a[0], a[1]) for a in agents], format_func=lambda a: a[0])
    print("AGENT =>", agent)
    
    # Only fetch aliases if we have a valid agent
    if agent and agent[0] != "-":
        aliases = get_aliases(agent_client, agent)
        if len(aliases) > 1:  # If we have more than just the default
            alias = st.selectbox("Aliases", options=aliases, format_func=lambda a: a[0])
        else:
            alias = aliases[0]
    else:
        aliases = [("-", "-")]
        alias = aliases[0]
    
    # Display session ID with option to reset
    st.text(f"Session ID: {get_session_id()[:8]}...")
    if st.button("New Session"):
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
        st.rerun()

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Process user input
if prompt := st.chat_input():
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Check if agent and alias are selected
    if agent[0] == "-" or alias[0] == "-":
        error_msg = "Please select a valid agent and alias before sending messages."
        st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    else:
        # Create a placeholder for streaming response
        response_placeholder = st.empty()
        message_placeholder = st.chat_message("assistant")
        
        try:
            # Invoke the agent
            response = agent_runtime_client.invoke_agent(
                agentId=agent[1],
                agentAliasId=alias[1],
                sessionId=get_session_id(),
                inputText=prompt,
            )
            
            print(f"RESPONSE => {response}")
            completion = ""
            
            # Process streaming response
            for event in response.get("completion", []):
                if "chunk" in event:
                    try:
                        chunk = event["chunk"]["bytes"].decode()
                        print(f"CHUNK => {chunk}")
                        completion += chunk
                        message_placeholder.write(completion)
                    except Exception as e:
                        print(f"Error processing chunk: {str(e)}")
            
            # Add assistant response to chat history
            if completion:
                st.session_state.messages.append({"role": "assistant", "content": completion})
            else:
                error_msg = "No response received from the agent."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
        except (ClientError, NoCredentialsError) as e:
            error_msg = f"Error invoking agent: {str(e)}"
            print(error_msg)
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
