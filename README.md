# tantan_webproject 홈트레이닝 스마트미러

### Dandan Smartmirror Project_Web

<img src="https://user-images.githubusercontent.com/31493835/139200109-0af92dd6-c1e5-451c-99cc-8636d6954762.png"  width="320" height="320"/><br>
한이음 프로젝트(공모전 입선)<br>
[프로젝트 영상 보러가기](https://youtu.be/Zfjd85sxkeU)<br>
[안드로이드 영상 보러가기](https://youtu.be/PzXwCY-_qAM)

## 목차<br>
[1. 소개](#소개)<br>
[2. 기획 의도](#기획-의도)<br>
[3. 주요 기능](#주요-기능)<br>
[4. 개발 기간](#개발-기간)<br>
[5. 팀원](#팀원)<br>
[6. 프로젝트 구조](#프로젝트-구조)<br>
[7. 스마트미러 설계도](#스마트미러-설계도)<br>
[8. 스마트미러](#스마트미러)<br>
[9. 스마트미러 동작 영상](#스마트미러-동작-영상)<br>
[10. API](#API)<br>

## 소개
- IoT 시스템 기반 스마트미러로 거울에 인공지능 서비스를 접목하여 음성인식으로 빠른 시간 안에 원하는 정보를 얻을 수 있습니다.
- 생활밀착형 스마트미러에 홈트레이닝 프로그램을 구현하여 집에서도 편하고 정확하게 운동할 수 있습니다.

## 기획 의도
- 코로나19 이후 홈트레이닝의 수요가 증가했지만, 혼자서 어떤 식으로 프로그램을 진행해야 하는지와 동작의 정확도를 모른채 운동하는 경우가 많다. 그러한 문제점을 해결하기 위해 운동 프로그램을 제시해주고, 잘못된 자세임을 실시간으로 피드백해주는 스마트미러를 기획하게 되었다.

## 주요 기능
- 날짜 및 시간, 달력 및 일정, 일기 예보 및 교통 보고서 정보 제공
- 홈트레이닝 서비스를 통해 집에서도 올바른 자세로 운동 가능
- 프로그램 종료 후 운동 종류, 시간, 횟수, 회차, 점수 확인
- 안드로이드 어플리케이션과 연결하면, 어플에서도 운동 기록 확인

## 개발 기간
- 2021년 02월 ~ 10월

## 팀원
- 🐶 [방세미](https://github.com/semibang) 
- 🐰 [임혜림](https://github.com/HyerimLim)
- 🐱 [차현경](https://github.com/CHA-HK)


## 프로젝트 구조
![프로젝트 흐름도](https://user-images.githubusercontent.com/31493835/139018333-284b23c8-17b4-4f99-88de-598ae87060a6.png)
- 전체적인 프로젝트 흐름은 다음과 같습니다. 
- 현재 깃은 스마트 미러 웹 페이지만 다루고 있으며 안드로이드와 관련한 깃은 하단 링크를 참조해주시길 바랍니다.
> https://github.com/971021hr/dandan_app_final

## 스마트미러 하드웨어 설계도

## 스마트미러 하드웨어

## 스마트미러 동작 영상

## API
- 미세먼지 http://openapi.seoul.go.kr:8088/(개인 인증키)/json/RealtimeCityAir/1/99
- 지하철 http://swopenapi.seoul.go.kr/api/subway/
- 구글 캘린더 
- 음성인식 웹스피치API
- 날씨 https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${WEATHER_KEY}&units=metric
