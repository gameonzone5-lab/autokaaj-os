package com.autokaaj.os

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private var uploadMessage: ValueCallback<Array<Uri>>? = null
    private val FILECHOOSER_RESULTCODE = 100

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        webView = WebView(this)
        setContentView(webView)

        val webSettings: WebSettings = webView.settings
        webSettings.javaScriptEnabled = true
        webSettings.domStorageEnabled = true
        webSettings.allowFileAccess = true
        webSettings.allowContentAccess = true

        webView.webViewClient = WebViewClient()
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                uploadMessage?.onReceiveValue(null)
                uploadMessage = null
                uploadMessage = filePathCallback

                val intent = fileChooserParams?.createIntent()
                try {
                    startActivityForResult(intent, FILECHOOSER_RESULTCODE)
                } catch (e: Exception) {
                    uploadMessage = null
                    return false
                }
                return true
            }
        }
        webView.loadUrl("https://app.roservicekolkata.info")
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == FILECHOOSER_RESULTCODE) {
            if (uploadMessage == null) return
            var results: Array<Uri>? = null
            if (resultCode == Activity.RESULT_OK && data != null) {
                val dataString = data.dataString
                if (dataString != null) {
                    results = arrayOf(Uri.parse(dataString))
                } else if (data.clipData != null) {
                    val count = data.clipData!!.itemCount
                    results = Array(count) { i -> data.clipData!!.getItemAt(i).uri }
                }
            }
            uploadMessage?.onReceiveValue(results)
            uploadMessage = null
        } else {
            super.onActivityResult(requestCode, resultCode, data)
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
