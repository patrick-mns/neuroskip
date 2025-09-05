console.log('[NEUROSKIP] Content script loaded on:', window.location.href);

class VideoSegmentSkipper {
    // #popup;
    #videoElement = null;
    #intervals = [];
    #alertElements = [];
    #timeUpdateListeners = [];
    #loadedDataListener = null;
    #activeAd = false;
    #activeIntro = false;
    #currentVideoSearch = window.location.search;

    constructor() {
        // this.#popup = this.#createPopup();
        this.#setupObservers();
        this.#initializeFromStorage();
    }

    // // Criação do popup de notificação
    // #createPopup() {
    //     const popup = document.createElement('div');
    //     Object.assign(popup.style, {
    //         position: 'fixed',
    //         right: '20px',
    //         bottom: '20px',
    //         backgroundColor: 'rgba(0, 0, 0, 0.8)',
    //         color: 'white',
    //         padding: '10px',
    //         borderRadius: '5px',
    //         display: 'none',
    //         zIndex: '99999999'
    //     });
    //     popup.id = 'skipPopup';
    //     document.body.appendChild(popup);
    //     return popup;
    // }

    // Obtém segmentos do vídeo
    async #fetchSegments(videoId) {
        console.log('fetchSegments called with videoId:', videoId);

        try {
            return new Promise((resolve, reject) => {
                console.log('Sending message to background script');
                chrome.runtime.sendMessage({ action: "getSegments", videoId }, response => {

                    console.log('Received response:', response);

                    if (chrome.runtime.lastError) {
                        console.error('Chrome runtime error:', chrome.runtime.lastError.message);
                        throw new Error(chrome.runtime.lastError.message);
                    }

                    if (!response?.data) {
                        console.log('No data in response');
                        return resolve(null);
                    }

                    if (response?.success && response?.data.data.segments) {
                        const segments = response.data.data.segments.map(segment => ({
                            start: Number(segment.start),
                            end: Number(segment.end),
                            type: segment.type
                        }));
                        console.info('Segments loaded:', segments.length, 'segments');
                        return resolve(segments);
                    }
                    console.log('Response not successful or no segments');
                    return resolve(null);
                });
            });
        } catch (error) {
            console.error('fetchSegments error:', error);
            // this.#popup.style.display = 'block';
            // this.#popup.textContent = `Error loading segments: ${error.message}`;
            return null;
        }
    }

    // Monitoramento do vídeo
    #monitorVideo(segments, video, progressBar) {
        const skipSegment = () => {
            if (!this.#activeAd && !this.#activeIntro) return;
            const currentTime = video.currentTime;

            segments.forEach(segment => {
                const shouldSkip = (segment.type === "ad" && this.#activeAd) ||
                    (segment.type === "intro" && this.#activeIntro);
                if (shouldSkip && currentTime >= segment.start && currentTime < segment.end) {
                    video.currentTime = segment.end;
                }
            });
        };

        video.addEventListener('timeupdate', skipSegment);
        this.#timeUpdateListeners.push(skipSegment);

        if (!progressBar) return;

        this.#loadedDataListener = () => {
            segments.forEach((segment, index) => {
                const shouldShow = (segment.type === "ad" && this.#activeAd) ||
                    (segment.type === "intro" && this.#activeIntro);
                if (shouldShow && !document.querySelector(`.alert-indicator-${segment.type}-${index}`)) {
                    this.#alertElements.push(
                        this.#createAlertBar(video, progressBar, segment)
                    );
                }
            });
        };

        this.#loadedDataListener();
        video.addEventListener('loadeddata', this.#loadedDataListener);
    }

    // Cria barra de alerta visual
    #createAlertBar(video, progressBar, { start, end, type }) {
        const totalDuration = video.duration;
        const progressBarWidth = progressBar.clientWidth;
        const color = type === "ad" ? 'yellow' : 'purple';
        const startPosition = (start / totalDuration) * progressBarWidth;
        const width = ((end - start) / totalDuration) * progressBarWidth;

        const alert = document.createElement('div');
        alert.className = `alert-indicator alert-indicator-${type}`;
        Object.assign(alert.style, {
            position: 'absolute',
            height: '4px',
            backgroundColor: color,
            left: `${startPosition}px`,
            width: `${width}px`
        });

        progressBar.appendChild(alert);
        return alert;
    }

    // Processamento dos segmentos
    async #processSegments(videoId) {

        // this.#popup.style.display = 'block';
        // this.#popup.textContent = `Processing (${videoId})...`;
        // this.#popup.style.display = 'none';
        const segments = await this.#fetchSegments(videoId);
        return segments;
    }

    // Inicialização
    async init() {

        if (!this.#activeAd) { return false }

        const urlParams = new URLSearchParams(window.location.search);
        const videoId = urlParams.get('v');
        if (!videoId) return;

        await this.#processSegmentsMonitor(videoId);
    }

    async #processSegmentsMonitor(videoId) {
        this.#videoElement = document.querySelector('video');
        if (!this.#videoElement) return;
        const segments = await this.#processSegments(videoId);
        if (segments) {
            this.#monitorVideo(segments, this.#videoElement, document.querySelector('.ytp-progress-bar'));
        }
    }

    // Limpeza
    #clear() {

        this.#intervals.forEach(clearInterval);
        this.#intervals.length = 0;
        this.#alertElements.forEach(el => el.remove());
        this.#alertElements.length = 0;
        // this.#popup.style.display = 'none';

        if (this.#videoElement) {
            this.#timeUpdateListeners.forEach(listener =>
                this.#videoElement.removeEventListener('timeupdate', listener));
            this.#timeUpdateListeners.length = 0;

            if (this.#loadedDataListener) {
                this.#videoElement.removeEventListener('loadeddata', this.#loadedDataListener);
                this.#loadedDataListener = null;
            }
        }

        chrome.runtime.sendMessage({ action: "abortController", controllerId: "getSegments" }, response => {});
    }

    // Observador de URL
    #setupObservers() {
        const urlObserver = new MutationObserver(() => {
            const newUrl = window.location.search;
            if (newUrl !== this.#currentVideoSearch && this.#activeAd == true) {
                this.#currentVideoSearch = newUrl;
                this.#clear();
                setTimeout(() => {
                    this.init();
                }, 500);
            }
        });
        urlObserver.observe(document, { subtree: true, childList: true });
        chrome.storage.onChanged.addListener((changes, namespace) => {
            if (namespace === "local" && changes.radarActive) {
                this.#activeAd = changes.radarActive.newValue.toggleInternalAd;
                this.#activeIntro = changes.radarActive.newValue.toggleSkipIntro;
                this.#clear();
                setTimeout(() => {
                    if (this.#activeAd || this.#activeIntro) this.init();
                }, 500);
            }
        });
    }

    // Inicialização a partir do storage
    #initializeFromStorage() {
        chrome.storage.local.get(['radarActive'], result => {
            this.#activeAd = result.radarActive?.toggleInternalAd || false;
            this.#activeIntro = result.radarActive?.toggleSkipIntro || false;
            if (this.#activeAd || this.#activeIntro) this.init();
        });
    }
}

console.log('[NEUROSKIP] Creating VideoSegmentSkipper instance');
try {
    new VideoSegmentSkipper();
    console.log('[NEUROSKIP] VideoSegmentSkipper instance created successfully');
} catch (error) {
    console.error('[NEUROSKIP] Error creating VideoSegmentSkipper:', error);
}