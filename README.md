# 코로나19 알림봇(Covid-19 alert discord bot)


### pre-script
python3.8, venv사용을 권장합니다.

```sh
python3.8 -m venv .venv
source ./.venv/bin/active
pip install -r requirements.txt
```

## 기능
기본 접두사는 ``!``입니다. 아래 서술할 접두사 변경 커맨드를 통해 봇의 접두사를 변경할 수 있습니다.

### 주 명령어
* **!도움**     
도움말을 출력합니다.
 
* **!현황 (시/도) (시/군/구) (국가) (세계)**    
지역을 입력하지 않으면 전국의 확진자 및 격리해제, 사망 현황을 불러옵니다.   
시/도를 입력하면 해당 지역의 현황을 불러옵니다.   
시/도 및 시/군/구를 입력하면 해당 지역의 확진자수를 불러옵니다.   
국가 이름을 입력하면 해당 국가의 코로나 현황을 불러옵니다.   
   
* **!지도 (지역)**    
입력한 지역의 확진자 동선을 보여줍니다.

* **!재난문자 (시/도)**    
입력한 지역의 재난문자를 보여줍니다.

* **!증상**    
코로나19의 증상과 적절한 대처방안을 불러옵니다.

### 설정 및 옵션
* **!위치설정 (시/도) (시/군/구)**    
내 위치를 등록합니다. 현황 등의 명령어에서 옵션을 입력할 필요가 없습니다.

* **!중요뉴스 (ㅇ/ㄴ)**    
이 옵션을 설정하면 중요 뉴스만 서버에 전달됩니다.

* **!방해금지 (ㅇ/ㄴ)**    
이 옵션을 설정하면 심야 시간에 뉴스가 전송되지 않습니다.

* **!채널설정 (#채널명)**    
뉴스를 전송하는 채널을 설정합니다.

* **!접두사설정 (접두사)**    
명령어 접두사를 변경합니다.

* **!접두사초기화**    
접두사를 ``!``으로 초기화합니다.

