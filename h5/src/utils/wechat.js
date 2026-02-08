/**
 * 微信JSSDK工具类
 * 用于微信公众号H5应用的JS-SDK功能封装
 */

import { request } from './request'

class WeChatSDK {
  constructor() {
    this.isReady = false
    this.isWeChatBrowser = this.checkIsWeChatBrowser()
    this.wx = null
  }

  /**
   * 检测是否在微信浏览器中
   */
  checkIsWeChatBrowser() {
    const ua = navigator.userAgent.toLowerCase()
    return ua.includes('micromessenger')
  }

  /**
   * 初始化微信JSSDK
   */
  async init() {
    if (!this.isWeChatBrowser) {
      console.warn('[微信SDK] 非微信浏览器环境，跳过初始化')
      return false
    }

    try {
      // 1. 动态加载微信JSSDK脚本
      await this.loadScript()
      this.wx = window.wx

      // 2. 从后端获取签名配置
      const config = await this.getJSSDKConfig()

      // 3. 配置微信JSSDK
      return await this.config(config)
    } catch (error) {
      console.error('[微信SDK] 初始化失败:', error)
      return false
    }
  }

  /**
   * 动态加载微信JSSDK脚本
   */
  loadScript() {
    return new Promise((resolve, reject) => {
      if (window.wx) {
        resolve()
        return
      }

      const script = document.createElement('script')
      script.src = 'https://res.wx.qq.com/open/js/jweixin-1.6.0.js'
      script.onload = resolve
      script.onerror = () => reject(new Error('微信JSSDK脚本加载失败'))
      document.head.appendChild(script)
    })
  }

  /**
   * 从后端获取JSSDK签名配置
   */
  async getJSSDKConfig() {
    try {
      const url = encodeURIComponent(window.location.href.split('#')[0])
      const response = await request.get(`/api/wechat/jssdk-config?url=${url}`)
      return response.data
    } catch (error) {
      console.error('[微信SDK] 获取签名配置失败:', error)
      throw error
    }
  }

  /**
   * 配置微信JSSDK
   */
  config(configData) {
    return new Promise((resolve, reject) => {
      this.wx.config({
        debug: false, // 生产环境设置为false
        appId: configData.appId,
        timestamp: configData.timestamp,
        nonceStr: configData.nonceStr,
        signature: configData.signature,
        jsApiList: [
          // 分享接口
          'updateAppMessageShareData',  // 分享给朋友
          'updateTimelineShareData',    // 分享到朋友圈
          'onMenuShareAppMessage',      // 旧版分享给朋友
          'onMenuShareTimeline',        // 旧版分享到朋友圈
          // 图片接口
          'chooseImage',                // 拍照或选择图片
          'previewImage',               // 预览图片
          'uploadImage',                // 上传图片
          'downloadImage',              // 下载图片
          // 位置接口
          'getLocation',                // 获取地理位置
          'openLocation',               // 查看地图位置
          // 扫一扫
          'scanQRCode'                  // 调起微信扫一扫
        ]
      })

      this.wx.ready(() => {
        this.isReady = true
        console.log('[微信SDK] 初始化成功 ✅')
        resolve(true)
      })

      this.wx.error((err) => {
        console.error('[微信SDK] 配置失败:', err)
        reject(err)
      })
    })
  }

  /**
   * 微信授权登录
   * @param {string} redirectUri - 回调地址
   * @param {string} state - 自定义参数
   */
  static login(redirectUri, state = 'STATE') {
    if (!redirectUri) {
      redirectUri = window.location.origin + '/wechat-callback'
    }
    
    // 从环境变量或配置文件获取AppID
    const appId = import.meta.env.VITE_WECHAT_APPID || 'YOUR_WECHAT_APPID'
    
    const url = `https://open.weixin.qq.com/connect/oauth2/authorize?` +
      `appid=${appId}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `response_type=code&` +
      `scope=snsapi_userinfo&` +
      `state=${state}#wechat_redirect`
    
    window.location.href = url
  }

  /**
   * 获取URL参数
   */
  static getUrlParam(name) {
    const reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)')
    const r = window.location.search.substr(1).match(reg)
    return r ? decodeURIComponent(r[2]) : null
  }

  /**
   * 处理微信授权回调
   */
  static async handleCallback() {
    const code = this.getUrlParam('code')
    const state = this.getUrlParam('state')
    
    if (code) {
      try {
        // 调用后端接口，用code换取用户信息和token
        const response = await request.post('/api/wechat/login', { code, state })
        return response.data
      } catch (error) {
        console.error('[微信登录] 回调处理失败:', error)
        throw error
      }
    }
    
    return null
  }

  /**
   * 分享给朋友
   */
  shareToFriend(options) {
    if (!this.isReady) {
      console.warn('[微信SDK] SDK未就绪，无法分享')
      return
    }

    const shareData = {
      title: options.title || 'TimeValue资产管理',
      desc: options.desc || '恒产生金 - AI驱动的个人资产管理系统',
      link: options.link || window.location.href,
      imgUrl: options.imgUrl || window.location.origin + '/logo.jpg',
      success: options.success || (() => console.log('分享成功')),
      cancel: options.cancel || (() => console.log('取消分享'))
    }

    this.wx.updateAppMessageShareData(shareData)
    // 兼容旧版接口
    this.wx.onMenuShareAppMessage(shareData)
  }

  /**
   * 分享到朋友圈
   */
  shareToTimeline(options) {
    if (!this.isReady) {
      console.warn('[微信SDK] SDK未就绪，无法分享')
      return
    }

    const shareData = {
      title: options.title || 'TimeValue资产管理 - 恒产生金',
      link: options.link || window.location.href,
      imgUrl: options.imgUrl || window.location.origin + '/logo.jpg',
      success: options.success || (() => console.log('分享成功')),
      cancel: options.cancel || (() => console.log('取消分享'))
    }

    this.wx.updateTimelineShareData(shareData)
    // 兼容旧版接口
    this.wx.onMenuShareTimeline(shareData)
  }

  /**
   * 选择图片
   */
  chooseImage(options = {}) {
    return new Promise((resolve, reject) => {
      if (!this.isReady) {
        reject(new Error('SDK未就绪'))
        return
      }

      this.wx.chooseImage({
        count: options.count || 1,
        sizeType: options.sizeType || ['compressed'],
        sourceType: options.sourceType || ['album', 'camera'],
        success: (res) => {
          resolve(res.localIds)
        },
        fail: reject
      })
    })
  }

  /**
   * 预览图片
   */
  previewImage(current, urls) {
    if (!this.isReady) {
      console.warn('[微信SDK] SDK未就绪')
      return
    }

    this.wx.previewImage({
      current,
      urls
    })
  }

  /**
   * 获取地理位置
   */
  getLocation() {
    return new Promise((resolve, reject) => {
      if (!this.isReady) {
        reject(new Error('SDK未就绪'))
        return
      }

      this.wx.getLocation({
        type: 'wgs84',
        success: resolve,
        fail: reject
      })
    })
  }

  /**
   * 扫一扫
   */
  scanQRCode() {
    return new Promise((resolve, reject) => {
      if (!this.isReady) {
        reject(new Error('SDK未就绪'))
        return
      }

      this.wx.scanQRCode({
        needResult: 1,
        scanType: ['qrCode', 'barCode'],
        success: (res) => {
          resolve(res.resultStr)
        },
        fail: reject
      })
    })
  }
}

// 创建单例
const wechatSDK = new WeChatSDK()

export default wechatSDK
