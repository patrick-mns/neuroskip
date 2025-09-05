const controllers = {};

const CONFIG = {
  BASE_URL: 'http://0.0.0.0:8000/v2/extension',
  VERSION: '0.0.1',
  MIN_INTERVAL: 10000
};

function getAccessToken() {
  return new Promise((resolve, reject) => {
    chrome.storage.local.get('access_token', ({ access_token }) => {
      if (!access_token) {
        reject(new Error("Internal Error"));
      } else {
        resolve(access_token);
      }
    });
  });
}

function withAccessToken(callback) {
  chrome.storage.local.get('access_token', ({ access_token }) => {
    if (!access_token) {
      throw new Error("Internal Error");
    }
    callback(access_token);
  });
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {

  if (message.action === "abortController") {
    const controller = controllers[message.controllerId];
    if (controller) {
      controller.abort();
      delete controllers[message.controllerId];
      sendResponse({ success: true });
    } else {
      sendResponse({ success: false, error: "No active fetch for this ID" });
    }
  }

  if (message.action === "getSegments") {
    getSegments(message, sendResponse);
    return true;
  }

  if (message.action === 'getAuthToken') {
    chrome.identity.getAuthToken({ interactive: true }, async (token) => {
      debugger;
      if (chrome.runtime.lastError) {
        sendResponse({ success: false, message: chrome.runtime.lastError.message });
        return;
      }
      try {
        let response = await fetch(`${CONFIG.BASE_URL}/login/google`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token }),
        });
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail);
        }
        let result = await response.json();
        const userInfo = result.data.userInfo;
        const access_token = result.data.access_token;
        chrome.storage.local.set({ userInfo }, () => {
          console.info('User information saved to local storage.');
        });
        chrome.storage.local.set({ access_token }, () => {
          console.info('Access token saved to local storage.');
        });
        sendResponse({ success: true, userInfo });
      } catch (error) {
        sendResponse({ success: false, message: error.message });
      }
    });
    return true;  // Indica que a resposta será assíncrona
  }

  if (message.action === "getUserInfo") {
    (async () => {
      try {
        withAccessToken(async (access_token) => {
          let response = await fetch(`${CONFIG.BASE_URL}/me`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${access_token}`,
            },
          });
          if (!response.ok) {
            let errorData = await response.json();
            throw new Error(errorData.detail);
          }
          let userInfo = await response.json();
          chrome.storage.local.set({ userInfo: userInfo.data }, () => {
            console.info('User information saved to local storage.');
          });
          sendResponse({ success: true, userInfo: userInfo.data  });
        })
      } catch (error) {
        sendResponse({ success: false, message: error.message });
      }
    })();
    return true;
  }

  if (message.action === "start_payment") {
    withAccessToken(async (access_token) => {
      try {
        let { amount } = message;
        const response = await fetch(`${CONFIG.BASE_URL}/create-checkout-session`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            'Authorization': `Bearer ${access_token}`,
          },
          body: JSON.stringify({ amount: amount })
        });
        const data = await response.json();
        if (data.checkout_url) {
          chrome.tabs.create({ url: data.checkout_url });
          sendResponse({ success: true });
        } else {
          console.error("No checkout_url received.");
          sendResponse({ success: false, error: "No checkout_url received." });
        }
      } catch (error) {
        console.error("Stripe session error:", error);
        sendResponse({ success: false, error: error.message });
      }
    });
    return true;
  }
});

function checkAndRemoveExpiredToken() {
  withAccessToken(async (access_token) => {
    try {
      const payload = JSON.parse(atob(access_token.split('.')[1]));
      const now = Math.floor(Date.now() / 1000);
      if (payload.exp && payload.exp < now) {
        chrome.storage.local.remove('access_token', () => {
          chrome.storage.local.remove('userInfo');
          chrome.identity.removeCachedAuthToken();
        });
      }
    } catch (e) {
      chrome.storage.local.remove('access_token', () => {
        console.warn('Failed to decode access token. Token removed.');
      });
    }
  });
}

setInterval(checkAndRemoveExpiredToken, 5 * 60 * 1000);


function getSegments(message, sendResponse) {
  const controller = new AbortController();
  const signal = controller.signal;
  controllers["getSegments"] = controller;
  
  (async () => {
    try {
      let { videoId } = message;
      console.log('getSegments called with videoId:', videoId);
      
      let token = await getAccessToken();
      console.log('Token retrieved:', token ? 'exists' : 'missing');

      const url = `${CONFIG.BASE_URL}/segments/${videoId}/youtube`;
      console.log('Making request to:', url);

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        signal,
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);
      
      if (!response.ok) {
        console.error('API Error:', data.detail || "Erro");
        throw new Error(data.detail || "Erro");
      }

      sendResponse({ status: response.status, success: true, data });
    } catch (err) {
      console.error('getSegments error:', err);
      if (err.name === "AbortError") {
        sendResponse({ success: false, error: "aborted" });
      } else {
        sendResponse({ success: false, error: err.message });
      }
    } finally {
      delete controllers["getSegments"]; // limpa depois
    }
  })();
}