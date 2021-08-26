$(document).ready(function (){

    console.log("speech test start!");


    if (typeof webkitSpeechRecognition !== 'function') {
        alert('크롬에서만 동작 합니다.');
        return false;
    }

    //음성 인식 받고 저장
    const FIRST_CHAR = /\S/;
    const TWO_LINE = /\n\n/g;
    const ONE_LINE = /\n/g;

    //Web Speech API 불러오기
    const recognition = new webkitSpeechRecognition();

    //한국어 입력
    const language = 'ko-KR';

    //html 에서 요소 가져오기_
    const $audio = document.querySelector('#audio');
    /*const $btnMic = document.querySelector('#btn-mic');*/
    const $resultWrap = document.querySelector('#result');
    const $btnSpeech = document.querySelector('#btn_speech');
    /*const $iconMusic = document.querySelector('#icon-music');*/



    let isRecognizing = false;
    let ignoreEndProcess = false;
    let finalTranscript = '';

    //continuous : true로 설정 할 경우, 각각 인식된 문장을 하나로 합쳐줌, 중간에 쉬어도 stop되지 않음.
    //interimResults : 실시간으로 인식된 결과 값을 모두 확인하고 싶다면 true를 설정하고, 최종 적으로 인식된 문장을 확인하고 싶다면 false를 작성
    recognition.continuous = true;
    recognition.interimResults = true;

    /**
     * 음성 인식 시작 처리
     */

    recognition.onstart = function () {
        console.log('onstart', arguments);
        isRecognizing = true;
        $btnSpeech.className = 'on';
        /*$btnMic.className = 'on';*/
    };

    /**
     * 음성 인식 종료 처리
     */
    recognition.onend = function () {
        console.log('onend', arguments);
        isRecognizing = false;

        if (ignoreEndProcess) {
            return false;
        }

        // DO end process
        $btnSpeech.className = 'off';
        /*$btnMic.className = 'off';*/
        if (!finalTranscript) {
            console.log('empty finalTranscript');
            return false;
        }
    };

    /**
     * 음성 인식 결과 처리
     */
    recognition.onresult = function (event) {
        console.log('onresult', event);

        let interimTranscript = '';
        if (typeof event.results === 'undefined') {
            recognition.onend = null;
            recognition.stop();
            return;
        }

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            const transcript = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        finalTranscript = capitalize(finalTranscript);
        final_span.innerHTML = linebreak(finalTranscript);
        interim_span.innerHTML = linebreak(interimTranscript);

        console.log('finalTranscript', finalTranscript);
        console.log('interimTranscript', interimTranscript);
        fireCommand(interimTranscript);
    };

    /**
     * 음성 인식 에러 처리
     */
    recognition.onerror = function (event) {
        console.log('onerror', event);

        if (event.error.match(/no-speech|audio-capture|not-allowed/)) {
            ignoreEndProcess = true;
        }

        $btnSpeech.className = 'off';
        /*$btnM

        ic.className = 'off';*/
    };

    /**
     * 명령어 처리
     * @param string
     */
    function fireCommand(string) {
        if (string.endsWith('레드')) {
            $resultWrap.className = 'red';
        } else if (string.endsWith('스피치') || string.endsWith('말해줘') || string.endsWith('말 해 줘') || string.endsWith('말해 줘')) {
            textToSpeech($('#final_span').text() || '전 음성 인식된 글자를 읽습니다.');
        } /*마지막 들어온 단어를 기준으로 함수 실행*/
        else if (string.endsWith('지하철')){
            showSubway();
        }else if (string.endsWith('달력')){
            showCalendar();
        }
        else if (string.endsWith('단단') || string.endsWith('탄탄')) {
            showDandanList();
        }
        else if (string.endsWith('하체') || string.endsWith('운동')){
            showDandan();
        }else if (string.endsWith('스쿼트') || string.endsWith('squat')){
            showDandanSquat();
        }else if (string.endsWith('다리')){
            alert('하체');
        }else if (string.endsWith('상체') || string.endsWith('상태')){
            showDandanUp();
        }else if (string.endsWith('종료') || string.endsWith('종묘')){
            showDandanQuit();
        }else if (string.endsWith('전신')){
            showDandanWhole();
        }else if (string.endsWith('요가')){
            showDandanYoga();
        }
    }

    /**
     * 개행 처리
     * @param {string} s
     */
    function linebreak(s) {
        return s.replace(TWO_LINE, '<p></p>').replace(ONE_LINE, '<br>');
    }

    /**
     * 첫문자를 대문자로 변환
     * @param {string} s
     */
    function capitalize(s) {
        return s.replace(FIRST_CHAR, function (m) {
            return m.toUpperCase();
        });
    }

    /**
     * 음성 인식 트리거
     */
    function start() {
        if (isRecognizing) {
            recognition.stop();
            return;
        }
        recognition.lang = language;
        recognition.start();
        ignoreEndProcess = false;

        finalTranscript = '';
        final_span.innerHTML = '';
        interim_span.innerHTML = '';
    }

    /**
     * 문자를 음성으로 읽어 줍니다.
     * 지원: 크롬, 사파리, 오페라, 엣지
     * 우린 이거 없어도 상관없음
     */
    function textToSpeech(text) {
        console.log('textToSpeech', arguments);

        // simple version
        speechSynthesis.speak(new SpeechSynthesisUtterance(text));
    }

    /**
     * 초기 바인딩
     * btn_speech 누를 시 작동이 여기 부분!
     */


    function initialize() {


        const $btnTTS = document.querySelector('#btn-tts');
        const defaultMsg = '전 음성 인식된 글자를 읽습니다.';

        $btnTTS.addEventListener('click', () => {
            const text = final_span.innerText || defaultMsg;
            textToSpeech(text);
        });

        /*$btnMic.addEventListener('click', start);*/
        $btnSpeech.addEventListener('click', start);

        autoStart();
    }

    function autoStart(){

        document.getElementById("btn_speech").click();

    }

    initialize();

});

function showSpeech(){

}