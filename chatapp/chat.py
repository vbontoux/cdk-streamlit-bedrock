import boto3
import streamlit as st
import json

st.session_state["i"] = 0 if "i" not in st.session_state else st.session_state["i"] + 1
print("Run #", st.session_state["i"])

def get_aliases(agent_client, agent):
    aliases = [("-", "-")]
    if agent[0] != "-":
        aliases = agent_client.list_agent_aliases(
            agentId=agent[1],
            maxResults=123
        )
        aliases = [(a["agentAliasName"], a["agentAliasId"]) for a in aliases["agentAliasSummaries"]]
    return aliases

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by Bedrock agents")

# Deal with Aliases
agent_client = boto3.client('bedrock-agent')
agent_runtime_client = boto3.client('bedrock-agent-runtime')

agents = [("-", "-")]
if "agents" not in st.session_state:
    agts = agent_client.list_agents(maxResults=123)
    print("AGTS =>", agts)
    if agts["agentSummaries"]:
        st.session_state["agents"] = [(a["agentName"], a["agentId"]) for a in agts["agentSummaries"]]
    else:
        st.session_state["agents"] = [("-", "-")]
print("AGENTS =>", st.session_state["agents"])
agents = st.session_state["agents"]
agent = None

# aliases = get_aliases(agent_client, agent)

with st.sidebar:
    agent = st.selectbox("agents", options=[(a[0], a[1]) for a in agents], format_func=lambda a: a[0])
    print("AGENT =>", agent)
    aliases = get_aliases(agent_client, agent)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = agent_runtime_client.invoke_agent(
                agentId=agent[1],
                agentAliasId= aliases[0][1],   # taking first alias for now
                sessionId="345",
                inputText=prompt,
            )
    print(f"RESPONSE => {response}")
    completion = ""
    for event in response.get("completion"):
      if "chunk" in event : 
        chunk = event["chunk"]["bytes"].decode()
        print(f"CHUNK => {chunk}")
        st.chat_message("assistant").write(chunk)
        completion = completion + chunk

    st.session_state.messages.append({"role": "assistant", "content": completion})
