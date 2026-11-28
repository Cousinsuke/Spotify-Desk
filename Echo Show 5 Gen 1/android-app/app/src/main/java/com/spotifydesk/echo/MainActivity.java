package com.spotifydesk.echo;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.ActivityNotFoundException;
import android.graphics.Color;
import android.net.Uri;
import android.net.http.SslError;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.webkit.CookieManager;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.SslErrorHandler;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.ScrollView;

public final class MainActivity extends Activity {
    private WebView web;
    private Uri origin;
    private boolean errorShown;
    private final Handler retryHandler = new Handler(Looper.getMainLooper());
    private int retryAttempt;
    private boolean retryPending;
    private boolean resumed;
    private long retryDelay;
    private final Runnable retryTask = () -> {
        if (resumed && retryPending && !isFinishing() && !isDestroyed()) openDashboard();
    };

    private void scheduleRetry() {
        retryHandler.removeCallbacks(retryTask);
        if (resumed && retryPending && !isFinishing() && !isDestroyed())
            retryHandler.postDelayed(retryTask, retryDelay);
    }

    private void retryNow() {
        retryAttempt = 0;
        openDashboard();
    }

    private static boolean retryableNetworkError(int code) {
        switch (code) {
            case WebViewClient.ERROR_HOST_LOOKUP:
            case WebViewClient.ERROR_CONNECT:
            case WebViewClient.ERROR_TIMEOUT:
            case WebViewClient.ERROR_IO:
            case WebViewClient.ERROR_UNKNOWN:
                return true;
            default:
                return false;
        }
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        origin = Uri.parse(getString(R.string.dashboard_origin));
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().setDecorFitsSystemWindows(false);
        openDashboard();
    }

    private void immersive() {
        WindowInsetsController c = getWindow().getInsetsController();
        if (c != null) {
            c.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            c.hide(WindowInsets.Type.systemBars());
        }
    }

    @Override public void onWindowFocusChanged(boolean focused) {
        super.onWindowFocusChanged(focused);
        if (focused) immersive();
    }

    private int port(Uri uri) { return uri.getPort() == -1 ? 443 : uri.getPort(); }

    private boolean allowed(Uri uri) {
        return uri != null && "https".equalsIgnoreCase(uri.getScheme())
            && origin.getHost().equalsIgnoreCase(uri.getHost())
            && port(origin) == port(uri) && uri.getUserInfo() == null;
    }

    private void openDashboard() {
        retryHandler.removeCallbacks(retryTask);
        retryPending = false;
        disposeWeb();
        errorShown = false;
        web = new WebView(this);
        web.setBackgroundColor(Color.BLACK);
        WebView.setWebContentsDebuggingEnabled(false);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setJavaScriptCanOpenWindowsAutomatically(false);
        s.setSupportMultipleWindows(false);
        s.setSafeBrowsingEnabled(true);
        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);
        cm.setAcceptThirdPartyCookies(web, false);
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest req) {
                return !allowed(req.getUrl());
            }
            @Override public void onPageStarted(WebView v, String url, android.graphics.Bitmap icon) {
                if (!allowed(Uri.parse(url))) {
                    v.stopLoading();
                    fail(v, "Blocked navigation outside the configured dashboard.");
                }
            }
            @Override public void onPageFinished(WebView v, String url) {
                if (v == web && !errorShown && allowed(Uri.parse(url))) {
                    CookieManager.getInstance().flush();
                    retryAttempt = 0;
                }
            }
            @Override public void onReceivedSslError(WebView v, SslErrorHandler handler, SslError error) {
                handler.cancel();
                fail(v, "HTTPS certificate validation failed. Check the Pi certificate and device clock. No connection was allowed.");
            }
            @Override public void onReceivedError(WebView v, WebResourceRequest req, WebResourceError error) {
                if (req.isForMainFrame()) {
                    int code = error.getErrorCode();
                    fail(v, "Dashboard unavailable. Check Wi-Fi, Pi service and HTTPS certificate. (Error " + code + ")",
                        retryableNetworkError(code));
                }
            }
            @Override public void onReceivedHttpError(WebView v, WebResourceRequest req, WebResourceResponse error) {
                if (req.isForMainFrame() && error.getStatusCode() >= 500)
                    fail(v, "Dashboard server unavailable. Check the Pi service. (HTTP " + error.getStatusCode() + ")",
                        RetryPolicy.retryableHttp(error.getStatusCode()));
            }
            @Override public boolean onRenderProcessGone(WebView v, RenderProcessGoneDetail detail) {
                fail(v, "WebView stopped. Tap Retry to reopen the dashboard.");
                return true;
            }
        });
        setContentView(web);
        web.loadUrl(origin.toString());
        immersive();
    }

    private void fail(WebView source, String message) {
        fail(source, message, false);
    }

    private void fail(WebView source, String message, boolean retryable) {
        if (source != web || errorShown || isFinishing() || isDestroyed()) return;
        errorShown = true;
        retryPending = retryable;
        if (retryable) {
            retryDelay = RetryPolicy.delayMillis(retryAttempt);
            if (retryAttempt < RetryPolicy.MAX_ATTEMPT) retryAttempt++;
            message += "\nAutomatic retry in " + (retryDelay / 1000) + " seconds.";
        }
        showRecovery(message);
        disposeWeb();
        scheduleRetry();
    }

    private void showRecovery(String message) {
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(28, 24, 28, 24);
        panel.setBackgroundColor(Color.rgb(24, 24, 24));
        TextView text = new TextView(this);
        text.setText("Spotify Desk\n\n" + message);
        text.setTextColor(Color.WHITE);
        text.setTextSize(18);
        panel.addView(text);
        Button retry = new Button(this);
        retry.setText("Retry dashboard");
        retry.setOnClickListener(v -> retryNow());
        panel.addView(retry);
        Button settings = new Button(this);
        settings.setText("Android settings");
        settings.setOnClickListener(v -> startActivity(new Intent(Settings.ACTION_SETTINGS)));
        panel.addView(settings);
        Button home = new Button(this);
        home.setText("Change default Home app");
        home.setOnClickListener(v -> openHomeSettings());
        panel.addView(home);
        Button exit = new Button(this);
        exit.setText("Exit");
        exit.setOnClickListener(v -> finish());
        panel.addView(exit);
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.addView(panel);
        setContentView(scroll);
    }

    private void disposeWeb() {
        if (web == null) return;
        WebView old = web;
        web = null;
        if (old.getParent() instanceof android.view.ViewGroup)
            ((android.view.ViewGroup) old.getParent()).removeView(old);
        old.destroy();
    }

    private void openHomeSettings() {
        try {
            startActivity(new Intent(Settings.ACTION_HOME_SETTINGS));
        } catch (ActivityNotFoundException e) {
            startActivity(new Intent(Settings.ACTION_SETTINGS));
        }
    }

    @Override public void onBackPressed() {
        retryHandler.removeCallbacks(retryTask);
        new AlertDialog.Builder(this).setTitle("Spotify Desk")
            .setItems(new String[]{"Return to dashboard", "Reload dashboard", "Android settings", "Change default Home app", "Exit"},
                (dialog, choice) -> {
                    if (choice == 1) retryNow();
                    else if (choice == 2) startActivity(new Intent(Settings.ACTION_SETTINGS));
                    else if (choice == 3) openHomeSettings();
                    else if (choice == 4) finish();
                }).setOnDismissListener(dialog -> scheduleRetry()).show();
    }

    @Override protected void onResume() {
        super.onResume();
        resumed = true;
        scheduleRetry();
    }

    @Override protected void onPause() {
        resumed = false;
        retryHandler.removeCallbacks(retryTask);
        CookieManager.getInstance().flush();
        super.onPause();
    }

    @Override protected void onDestroy() {
        resumed = false;
        retryPending = false;
        retryHandler.removeCallbacks(retryTask);
        disposeWeb();
        super.onDestroy();
    }
}
