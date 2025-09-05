const toggleButtons = document.querySelectorAll('.toggleButton');
const radarContainer = document.querySelector('.radar-container');
const signInButton = document.getElementById('signInButton');
const signOutButton = document.getElementById('signOutButton');
const userInfoDiv = document.getElementById('userInfo');
const adContainer = document.getElementById('ad-container');
const payBtn = document.getElementById('payBtn');
const customAmount = document.getElementById('customAmount');
const alertContainer = document.getElementById('alert-container');
const alertText = document.getElementById('alert-text');
const closeAlert = document.getElementById('close-alert');

const CONFIG = {
  BASE_URL: 'http://0.0.0.0:8000/v2/extension',
  VERSION: '0.0.1',
};

function getToggleState() {
  return Array.from(toggleButtons).reduce((acc, btn) => {
    acc[btn.id] = btn.checked;
    return acc;
  }, {});
}

function updateRadarState(state = null) {
  const activeButtons = state || getToggleState();
  const anyChecked = Object.values(activeButtons).some(Boolean);
  radarContainer.classList.toggle('active', anyChecked);
  chrome.storage.local.set({ radarActive: activeButtons });
}

function enableToggleButtons() {
  toggleButtons.forEach(btn => btn.disabled = false);
}

function restoreToggleState() {
  chrome.storage.local.get(['radarActive'], ({ radarActive = {} }) => {
    toggleButtons.forEach(btn => {
      btn.checked = !!radarActive[btn.id];
    });
    updateRadarState(radarActive);
    enableToggleButtons();
  });
}

function showUserInfo(userInfo) {
  if(!userInfo) return;

  userInfoDiv.innerHTML = `
      <div  style="display: flex; align-items: center; gap: 10px; width: 60%;">
        <img src="${userInfo.picture}" alt="Avatar" style="width: 20px; height: 20px; border-radius: 50%;">
        <span style="">${userInfo.given_name}</span>
      </div>
  `;
  signInButton.style.display = 'none';
  signOutButton.style.display = 'inline-block';
  adContainer.style.display = 'block';
}

function resetUI() {
  chrome.storage.local.remove('userInfo');
  chrome.storage.local.remove('access_token');
  toggleButtons.forEach(btn => btn.disabled = true);
  userInfoDiv.innerHTML = '';
  signInButton.style.display = 'inline-block';
  signOutButton.style.display = 'none';
  adContainer.style.display = 'none';
  updateRadarState({});
  enableToggleButtons();
}

toggleButtons.forEach(btn => {
  btn.addEventListener('change', () => {
    updateRadarState();
    enableToggleButtons();
  });
});

signInButton.addEventListener('click', () => {
  debugger;
  chrome.runtime.sendMessage({ action: 'getAuthToken' }, (response) => {
    if (response.success) {
      console.log(response);
      showUserInfo(response.userInfo);
    } else {
      resetUI();
      console.warn(response.message);
    }
  });
});

signOutButton.addEventListener('click', () => {
  chrome.identity.getAuthToken({ interactive: false }, (token) => {
    if (!token) {
      resetUI();
      return;
    }
    fetch(`https://accounts.google.com/o/oauth2/revoke?token=${token}`)
      .then(() => {
        chrome.identity.removeCachedAuthToken({ token }, () => {
          chrome.storage.local.remove('userInfo');
          chrome.storage.local.remove('access_token');
          resetUI();
        });
      })
      .catch(console.warn);
  });
});

// payBtn.addEventListener("click", () => {
//   let amount = parseFloat(customAmount.value) ?? 10.00;
//   if(amount > 0 == 0){ return }
//   chrome.runtime.sendMessage({ action: "start_payment", amount: amount }, () => {
//     console.info("Opening payment page in a new window...");
//   });
// });

chrome.storage.local.get('access_token', ({ access_token }) => {
  if (access_token) {
    chrome.storage.local.get('userInfo', async ({ userInfo }) => {
      if (userInfo) {
        showUserInfo(userInfo);
        chrome.runtime.sendMessage({ action: 'getUserInfo', access_token }, (response) => {
          if (response && response.success && response.userInfo) {
            return chrome.storage.local.set({ userInfo: response.userInfo }, () => {
              showUserInfo(response.userInfo);
              console.info('User information saved to local storage.');
            });
          }
          return resetUI();
        });
      }
      else {
        return resetUI();
      }
    });
    return;
  }
  return resetUI();
});

restoreToggleState();

closeAlert.addEventListener("click", () => {
  alertContainer.style.display = 'none';
  alertText.innerHTML = '...';
});

function clearAlert(){
  alertContainer.style.display = 'none';
  alertText.innerHTML = null;
};

function showAlert(message){
  alertContainer.style.display = 'block';
  alertText.innerHTML = message;
};