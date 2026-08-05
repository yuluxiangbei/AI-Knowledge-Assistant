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
      message.value = isLogin.value ? '登录成功' : '注册成功'
    } catch (error) {
      // 失败:显示后端返回的错误信息(detail 字段)
      // error.response?.data?.detail:可选链,后端 401/409 的 detail
      message.value = '错误' + (error.response?.data?.detail || error.message)
    }
  }

  // ---- 上传文档 ----
  async function uploadFile() {
  
    const formData =  new FormData()                     // 构造表单数据(文件专用格式)
    formData.append('file', selectedFile.value)    // 字段名'file'要和后端参数一致
    // ⚠️ 问题2:URL 少了 documents,应该是 /api/v1/documents/upload
    const res = await axios.post('http://localhost:8000/api/v1/documents/upload', formData, {
      headers: {
        // 带 token 认证:Bearer <token> 格式
        'Authorization': `Bearer ${token.value}`
      }
      // 注意:不手动设 Content-Type,axios 检测到 FormData 自动加 multipart
    })
    // ⚠️ 问题3:上传成功后没有刷新列表,应该调用 loadDocuments()
    await loadDocuments()
  }

  // ---- 加载文档列表 ----
  async function loadDocuments() {
    // GET 请求,带 token
    const res = await axios.get('http://localhost:8000/api/v1/documents', {
      headers: {
        'Authorization': `Bearer ${token.value}`
      }
    })
    documents.value = res.data   // 后端返回数组,赋给列表
  }
</script>

<template>
  <section id="center">
    <h1>"AI智能知识助手"</h1>
    <!-- 模式切换 -->
    <!-- v-if="!token":没登录(空)显示登录表单 -->
    <div v-if="!token">
      <!-- 点击切换登录/注册模式 -->
      <button @click="isLogin = !isLogin">
        {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
      </button>
      <!-- v-model:输入框和变量双向绑定 -->
      <input v-model="username" placeholder="用户名" />
      <input v-model="password" type="password" placeholder="密码" />
      <button @click="submit">{{ isLogin ? '登录' : '注册' }}</button>
      <p>{{ message }}</p>
    </div>
    <!-- v-else:已登录显示上传区 -->
    <div v-else>
      <h2>已登录</h2>
      <!-- @change:文件选择变化时触发 onFileChange -->
      <input type ="file" @change="onFileChange" />
      <button @click="uploadFile">上传文件</button>
      <!-- v-for:遍历 documents 数组渲染列表,:key 给唯一标识 -->
      <ul>
        <li v-for="doc in documents" :key="doc.id">{{ doc.filename }}</li>
      </ul>
      <!-- 退出:清 token + 清 localStorage -->
      <button @click="token = ''; localStorage.removeItem('token')"> 退出登录 </button>
    </div>
  </section>
</template>
