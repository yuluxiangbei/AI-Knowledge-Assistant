<script setup>
  // ===== Vue 3 组合式 API:所有逻辑写在这里 =====
  import { ref } from 'vue'        // ref:创建响应式变量(变了页面自动更新)
  import axios from 'axios'        // axios:发 HTTP 请求的库

  // ---- 登录/注册表单数据 ----
  const username = ref('')         // 用户名输入框绑定
  const password = ref('')         // 密码输入框绑定
  const isLogin = ref(true)        // 模式切换:true=登录,false=注册
  const message = ref('')          // 提示信息(成功/错误)

  // ---- 登录状态 ----
  // token 从 localStorage 初始化:刷新页面不丢登录状态(Streamlit 的教训)
  const token = ref(localStorage.getItem('token') || "")

  // ---- 上传相关 ----
  const selectedFile = ref(null)   // 用户选中的文件对象
  const documents = ref([])        // 已上传文档列表(数组)
  const conversations = ref([])    // 会话列表(数组)

  const currentConv = ref(null)    // 当前选中的会话
  const messages = ref([])         // 当前会话的消息
  const inputText = ref('')        // 输入框内容
  const sending = ref(false)       // 发送中状态

  // 文件选择框变化时触发:把选中的文件存起来
  function onFileChange(event) {
    selectedFile.value = event.target.files[0]   // files[0] = 第一个文件
  }

  // ---- 登录/注册提交 ----
  async function submit(){
    // 根据模式选 URL:三元表达式,true 走登录,false 走注册
    const url = isLogin.value
     ? 'http://localhost:8000/api/v1/auth/login'
     : 'http://localhost:8000/api/v1/auth/register'

    try{
      // 发 POST 请求,body 是 {username, password} JSON
      const res = await axios.post(url, {
        username: username.value,
        password: password.value
      })
      // 成功:存 token(内存 ref + localStorage 双份)
      token.value = res.data.access_token          // 响应里的 access_token
      localStorage.setItem('token', token.value)   // 持久化,刷新不丢
      message.value = ''
      loadDocuments()   // 登录/注册成功后加载文档列表
      loadConversations() // 登录/注册成功后加载会话列表
    } catch (error) {
      // 失败:显示后端返回的错误信息(detail 字段)
      message.value = '错误' + (error.response?.data?.detail || error.message)
    }
  }

  // 退出登录
  function logout() {
    token.value = ''
    localStorage.removeItem('token')
    conversations.value = []
    currentConv.value = null
    messages.value = []
    documents.value = []
    message.value = ''
  }

  // ---- 上传文档 ----
  async function uploadFile() {
    if (!selectedFile.value) { message.value = '请先选择文件'; return }
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    try {
      await axios.post('http://localhost:8000/api/v1/documents/upload', formData, {
        headers: { 'Authorization': `Bearer ${token.value}` }
      })
      message.value = '上传成功'
      selectedFile.value = null
      await loadDocuments()
    } catch (error) {
      message.value = '上传失败:' + (error.response?.data?.detail || error.message)
    }
  }

  // 删除文档
  async function deleteDocument(doc) {
    await axios.delete(`http://localhost:8000/api/v1/documents/${doc.id}`, {
      headers: { 'Authorization': `Bearer ${token.value}` }
    })
    documents.value = documents.value.filter(d => d.id !== doc.id)
  }

  // ---- 加载文档列表 ----
  async function loadDocuments() {
    const res = await axios.get('http://localhost:8000/api/v1/documents', {
      headers: { 'Authorization': `Bearer ${token.value}` }
    })
    documents.value = res.data
  }

  // ---- 加载会话列表 ----
  async function loadConversations() {
    const res = await axios.get('http://localhost:8000/api/v1/conversations', {
      headers: { 'Authorization': `Bearer ${token.value}` }
    })
    conversations.value = res.data
    // 自动选中第一个会话
    if (conversations.value.length > 0) {
      selectConversation(conversations.value[0])
    }
  }

  // 新建会话
  async function newConversation() {
    const res = await axios.post('http://localhost:8000/api/v1/conversations',
      {title: '新会话'},
      {headers: {'Authorization': `Bearer ${token.value}`}}
    )
    conversations.value.unshift(res.data) // 新会话加到最前面
    selectConversation(res.data)          // 自动选中新会话
  }

  // 选中会话:加载它的消息
  async function selectConversation(conv){
    currentConv.value = conv
    const res = await axios.get(`http://localhost:8000/api/v1/conversations/${conv.id}/messages`, {
      headers: {'Authorization': `Bearer ${token.value}`}
    })
    messages.value = res.data
  }

  // 删除会话
  async function deleteConversation(conv){
    await axios.delete(`http://localhost:8000/api/v1/conversations/${conv.id}`, {
      headers: {'Authorization': `Bearer ${token.value}`}
    })
    // 从列表移除
    conversations.value = conversations.value.filter(c => c.id !== conv.id)
    if (currentConv.value?.id === conv.id) {
      currentConv.value = null
      messages.value = []
    }
  }


  // 发送消息
  async function sendMessage(){
    if(!inputText.value.trim() || !currentConv.value || sending.value) return
    const text = inputText.value
    inputText.value = ''
    sending.value = true
    try {
      // 先显示用户消息(乐观更新)
      messages.value.push({ role: 'user', content: text, id: Date.now(), created_at: new Date().toISOString() })
      const res = await axios.post(
        `http://localhost:8000/api/v1/conversations/${currentConv.value.id}/messages`,
        {content: text},
        {headers: {'Authorization': `Bearer ${token.value}`}}
      )
      // 追加 AI 回答(带 sources)
      messages.value.push(res.data)
    } catch (error) {
      messages.value.push({ role: 'assistant', content: '出错了:' + (error.response?.data?.detail || error.message), id: Date.now(), created_at: new Date().toISOString() })
    } finally {
      sending.value = false
    }
  }

  // 回车发送(Shift+Enter 换行)
  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }
</script>

<template>
  <!-- ================= 主界面:ChatGPT 风格 ================= -->
  <div class="app-layout">

    <!-- 左侧栏 -->
    <aside class="sidebar">
      <button class="new-chat-btn" @click="newConversation">✦ 新对话</button>

      <!-- 会话列表 -->
      <div class="conv-list">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          class="conv-item"
          :class="{ active: currentConv?.id === conv.id }"
          @click="selectConversation(conv)"
        >
          <span class="conv-title">{{ conv.title }}</span>
          <button class ="del-btn" @click.stop="deleteConversation(conv)">🗑️</button>
        </div>
        <p v-if="conversations.length === 0" class="empty-tip">暂无会话</p>
      </div>

      <!-- 左下角:未登录显示登录/注册表单 -->
      <div v-if="!token" class="sidebar-footer">
        <button class="switch-btn" @click="isLogin = !isLogin">
          {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
        </button>
        <input v-model="username" placeholder="用户名" autocomplete="off" />
        <input v-model="password" type="password" placeholder="密码" autocomplete="off" @keydown.enter="submit" />
        <button class="login-btn" @click="submit">{{ isLogin ? '登录' : '注册' }}</button>
        <p class="msg">{{ message }}</p>
      </div>

      <!-- 左下角:已登录显示上传+退出 -->
      <div v-else class="sidebar-footer">
        <input id="fileInput" type="file" @change="onFileChange" />
        <button class="upload-btn" @click="uploadFile">📤 上传文档</button>
        <!-- 文档列表 -->
        <ul>
          <li v-for="doc in documents" :key="doc.id">
            {{ doc.filename }}
            <button @click="deleteDocument(doc)">删除</button>
          </li>
        </ul>
        <p class="upload-msg">{{ message }}</p>
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </aside>

    <!-- 右侧主区 -->
    <main class="chat-area">
      <!-- 对话记录 -->
      <div class="messages">
        <div v-if="!token" class="welcome">
          <h2>欢迎使用 AI 智能知识助手</h2>
          <p>请在左侧登录或注册</p>
        </div>

        <div v-else-if="messages.length === 0" class="welcome">
          <h2>有什么可以帮你？</h2>
          <p>上传文档后，我可以基于你的资料回答问题</p>
        </div>

        <div v-for="msg in messages" :key="msg.id" class="msg-row" :class="msg.role">
          <div class="msg-avatar">{{ msg.role === 'user' ? '🧑' : '🤖' }}</div>
          <div class="msg-content">
            <div class="msg-bubble">{{ msg.content }}</div>
            <!-- 引用来源展示 -->
            <div v-if="msg.role === 'assistant' && msg.sources && msg.sources.length" class="sources">
              <span class="sources-title">📎 引用来源</span>
              <span v-for="(src, i) in msg.sources" :key="i" class="source-tag">
                {{ src.filename }} (块{{ src.chunk_index }})
              </span>
            </div>
          </div>
        </div>

        <!-- 正在思考 -->
        <div v-if="sending" class="msg-row assistant">
          <div class="msg-avatar">🤖</div>
          <div class="msg-content">
            <div class="msg-bubble typing">正在思考…</div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-area">
        <textarea
          v-model="inputText"
          placeholder="输入消息…(Enter 发送)"
          rows="2"
          :disabled="!token"
          @keydown="handleKeydown"
        ></textarea>
        <button class="send-btn" :disabled="!token || sending" @click="sendMessage">发送</button>
      </div>
    </main>

  </div>
</template>
