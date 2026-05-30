package com.autokaaj.os

import android.app.Activity
import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.webViewClient = WebViewClient()
        // এটি আপনার টার্মাক্সের লোকালহোস্টের সাথে কানেক্ট করবে
        webView.loadUrl("https://app.roservicekolkata.info") 
        setContentView(webView)
    }
}
