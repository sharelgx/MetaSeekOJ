<template>
  <el-form :model="ruleForm2" :rules="rules2" ref="ruleForm2" label-position="left" label-width="0px"
           class="demo-ruleForm login-container">
    <h3 class="title">{{$t('m.Welcome_to_Login')}} - 管理员登录</h3>
    <el-form-item prop="account">
      <el-input type="text" v-model="ruleForm2.account" auto-complete="off" :placeholder="$t('m.username')" @keyup.enter.native="handleLogin"></el-input>
    </el-form-item>
    <el-form-item prop="password">
      <el-input type="password" v-model="ruleForm2.password" auto-complete="off" :placeholder="$t('m.password')" @keyup.enter.native="handleLogin"></el-input>
    </el-form-item>
    <el-form-item style="width:100%;">
      <el-button type="primary" style="width:100%;" @click.native.prevent="handleLogin" :loading="logining">{{$t('m.GO')}}
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script>
  import api from '../../api'
  import types from '@/store/types'

  export default {
    data () {
      return {
        logining: false,
        ruleForm2: {
          account: '',
          password: ''
        },
        rules2: {
          account: [
            {required: true, trigger: 'blur'}
          ],
          password: [
            {required: true, trigger: 'blur'}
          ]
        },
        checked: true
      }
    },
    methods: {
      handleLogin (ev) {
        this.$refs.ruleForm2.validate((valid) => {
          if (valid) {
            this.logining = true
            // 调用登录API - 测试登录功能
            api.login(this.ruleForm2.account, this.ruleForm2.password).then(async (data) => {
              try {
                // 登录成功后获取用户profile并更新store状态
                const profileRes = await api.getProfile()
                if (profileRes.data.data) {
                  this.$store.commit(types.CHANGE_PROFILE, {profile: profileRes.data.data})
                  console.log('Login successful, profile updated:', profileRes.data.data)
                }
                
                this.logining = false
                // 检查是否有重定向路径，如果有则跳转到原来的页面，否则跳转到dashboard
                const redirect = this.$route.query.redirect || '/'
                this.$router.push(redirect)
              } catch (err) {
                console.error('Failed to get profile after login:', err)
                this.logining = false
                // 即使获取profile失败，也跳转到目标页面，让页面自己处理认证
                const redirect = this.$route.query.redirect || '/'
                this.$router.push(redirect)
              }
            }, () => {
              this.logining = false
            })
          } else {
            this.$error('Please check the error fields')
          }
        })
      }
    }
  }
</script>

<style lang="less" scoped>
  .login-container {
    /*box-shadow: 0 0px 8px 0 rgba(0, 0, 0, 0.06), 0 1px 0px 0 rgba(0, 0, 0, 0.02);*/
    -webkit-border-radius: 5px;
    border-radius: 5px;
    -moz-border-radius: 5px;
    background-clip: padding-box;
    margin: 180px auto;
    width: 350px;
    padding: 35px 35px 15px 35px;
    background: #fff;
    border: 1px solid #eaeaea;
    box-shadow: 0 0 25px #cac6c6;
    .title {
      margin: 0px auto 40px auto;
      text-align: center;
      color: #505458;
    }
    .remember {
      margin: 0px 0px 35px 0px;
    }
  }
</style>
