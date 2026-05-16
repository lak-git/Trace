---
name: create-a-project
description: Information regarding creating a project in plane.
---

POST/api/v1/workspaces/{workspace\_slug}/projects/

Create a new project in the workspace with default states and member assignments.

### Path Parameters [​](#path-parameters)

`workspace_slug`:requiredstring

The workspace\_slug represents the unique workspace identifier for a workspace in Plane. It can be found in the URL. For example, in the URL `https://app.plane.so/my-team/projects/`, the workspace slug is `my-team`.

### Body Parameters [​](#body-parameters)

`description`:optionalstring

Description.

`project_lead`:optionalstring

Project lead.

`default_assignee`:optionalstring

Default assignee.

`identifier`:requiredstring

Identifier.

`icon_prop`:optionalobject

Icon prop.

`emoji`:optionalstring

Emoji.

`cover_image`:optionalstring

Cover image.

`module_view`:optionalboolean

Module view.

`cycle_view`:optionalboolean

Cycle view.

`issue_views_view`:optionalboolean

Issue views view.

`page_view`:optionalboolean

Page view.

`intake_view`:optionalboolean

Intake view.

`guest_view_all_features`:optionalboolean

Guest view all features.

`archive_in`:optionalinteger

Archive in.

`close_in`:optionalinteger

Close in.

`timezone`:optionalstring

*   `Africa/Abidjan` - Africa/Abidjan
*   `Africa/Accra` - Africa/Accra
*   `Africa/Addis_Ababa` - Africa/Addis\_Ababa
*   `Africa/Algiers` - Africa/Algiers
*   `Africa/Asmara` - Africa/Asmara
*   `Africa/Bamako` - Africa/Bamako
*   `Africa/Bangui` - Africa/Bangui
*   `Africa/Banjul` - Africa/Banjul
*   `Africa/Bissau` - Africa/Bissau
*   `Africa/Blantyre` - Africa/Blantyre
*   `Africa/Brazzaville` - Africa/Brazzaville
*   `Africa/Bujumbura` - Africa/Bujumbura
*   `Africa/Cairo` - Africa/Cairo
*   `Africa/Casablanca` - Africa/Casablanca
*   `Africa/Ceuta` - Africa/Ceuta
*   `Africa/Conakry` - Africa/Conakry
*   `Africa/Dakar` - Africa/Dakar
*   `Africa/Dar_es_Salaam` - Africa/Dar\_es\_Salaam
*   `Africa/Djibouti` - Africa/Djibouti
*   `Africa/Douala` - Africa/Douala
*   `Africa/El_Aaiun` - Africa/El\_Aaiun
*   `Africa/Freetown` - Africa/Freetown
*   `Africa/Gaborone` - Africa/Gaborone
*   `Africa/Harare` - Africa/Harare
*   `Africa/Johannesburg` - Africa/Johannesburg
*   `Africa/Juba` - Africa/Juba
*   `Africa/Kampala` - Africa/Kampala
*   `Africa/Khartoum` - Africa/Khartoum
*   `Africa/Kigali` - Africa/Kigali
*   `Africa/Kinshasa` - Africa/Kinshasa
*   `Africa/Lagos` - Africa/Lagos
*   `Africa/Libreville` - Africa/Libreville
*   `Africa/Lome` - Africa/Lome
*   `Africa/Luanda` - Africa/Luanda
*   `Africa/Lubumbashi` - Africa/Lubumbashi
*   `Africa/Lusaka` - Africa/Lusaka
*   `Africa/Malabo` - Africa/Malabo
*   `Africa/Maputo` - Africa/Maputo
*   `Africa/Maseru` - Africa/Maseru
*   `Africa/Mbabane` - Africa/Mbabane
*   `Africa/Mogadishu` - Africa/Mogadishu
*   `Africa/Monrovia` - Africa/Monrovia
*   `Africa/Nairobi` - Africa/Nairobi
*   `Africa/Ndjamena` - Africa/Ndjamena
*   `Africa/Niamey` - Africa/Niamey
*   `Africa/Nouakchott` - Africa/Nouakchott
*   `Africa/Ouagadougou` - Africa/Ouagadougou
*   `Africa/Porto-Novo` - Africa/Porto-Novo
*   `Africa/Sao_Tome` - Africa/Sao\_Tome
*   `Africa/Tripoli` - Africa/Tripoli
*   `Africa/Tunis` - Africa/Tunis
*   `Africa/Windhoek` - Africa/Windhoek
*   `America/Adak` - America/Adak
*   `America/Anchorage` - America/Anchorage
*   `America/Anguilla` - America/Anguilla
*   `America/Antigua` - America/Antigua
*   `America/Araguaina` - America/Araguaina
*   `America/Argentina/Buenos_Aires` - America/Argentina/Buenos\_Aires
*   `America/Argentina/Catamarca` - America/Argentina/Catamarca
*   `America/Argentina/Cordoba` - America/Argentina/Cordoba
*   `America/Argentina/Jujuy` - America/Argentina/Jujuy
*   `America/Argentina/La_Rioja` - America/Argentina/La\_Rioja
*   `America/Argentina/Mendoza` - America/Argentina/Mendoza
*   `America/Argentina/Rio_Gallegos` - America/Argentina/Rio\_Gallegos
*   `America/Argentina/Salta` - America/Argentina/Salta
*   `America/Argentina/San_Juan` - America/Argentina/San\_Juan
*   `America/Argentina/San_Luis` - America/Argentina/San\_Luis
*   `America/Argentina/Tucuman` - America/Argentina/Tucuman
*   `America/Argentina/Ushuaia` - America/Argentina/Ushuaia
*   `America/Aruba` - America/Aruba
*   `America/Asuncion` - America/Asuncion
*   `America/Atikokan` - America/Atikokan
*   `America/Bahia` - America/Bahia
*   `America/Bahia_Banderas` - America/Bahia\_Banderas
*   `America/Barbados` - America/Barbados
*   `America/Belem` - America/Belem
*   `America/Belize` - America/Belize
*   `America/Blanc-Sablon` - America/Blanc-Sablon
*   `America/Boa_Vista` - America/Boa\_Vista
*   `America/Bogota` - America/Bogota
*   `America/Boise` - America/Boise
*   `America/Cambridge_Bay` - America/Cambridge\_Bay
*   `America/Campo_Grande` - America/Campo\_Grande
*   `America/Cancun` - America/Cancun
*   `America/Caracas` - America/Caracas
*   `America/Cayenne` - America/Cayenne
*   `America/Cayman` - America/Cayman
*   `America/Chicago` - America/Chicago
*   `America/Chihuahua` - America/Chihuahua
*   `America/Ciudad_Juarez` - America/Ciudad\_Juarez
*   `America/Costa_Rica` - America/Costa\_Rica
*   `America/Creston` - America/Creston
*   `America/Cuiaba` - America/Cuiaba
*   `America/Curacao` - America/Curacao
*   `America/Danmarkshavn` - America/Danmarkshavn
*   `America/Dawson` - America/Dawson
*   `America/Dawson_Creek` - America/Dawson\_Creek
*   `America/Denver` - America/Denver
*   `America/Detroit` - America/Detroit
*   `America/Dominica` - America/Dominica
*   `America/Edmonton` - America/Edmonton
*   `America/Eirunepe` - America/Eirunepe
*   `America/El_Salvador` - America/El\_Salvador
*   `America/Fort_Nelson` - America/Fort\_Nelson
*   `America/Fortaleza` - America/Fortaleza
*   `America/Glace_Bay` - America/Glace\_Bay
*   `America/Goose_Bay` - America/Goose\_Bay
*   `America/Grand_Turk` - America/Grand\_Turk
*   `America/Grenada` - America/Grenada
*   `America/Guadeloupe` - America/Guadeloupe
*   `America/Guatemala` - America/Guatemala
*   `America/Guayaquil` - America/Guayaquil
*   `America/Guyana` - America/Guyana
*   `America/Halifax` - America/Halifax
*   `America/Havana` - America/Havana
*   `America/Hermosillo` - America/Hermosillo
*   `America/Indiana/Indianapolis` - America/Indiana/Indianapolis
*   `America/Indiana/Knox` - America/Indiana/Knox
*   `America/Indiana/Marengo` - America/Indiana/Marengo
*   `America/Indiana/Petersburg` - America/Indiana/Petersburg
*   `America/Indiana/Tell_City` - America/Indiana/Tell\_City
*   `America/Indiana/Vevay` - America/Indiana/Vevay
*   `America/Indiana/Vincennes` - America/Indiana/Vincennes
*   `America/Indiana/Winamac` - America/Indiana/Winamac
*   `America/Inuvik` - America/Inuvik
*   `America/Iqaluit` - America/Iqaluit
*   `America/Jamaica` - America/Jamaica
*   `America/Juneau` - America/Juneau
*   `America/Kentucky/Louisville` - America/Kentucky/Louisville
*   `America/Kentucky/Monticello` - America/Kentucky/Monticello
*   `America/Kralendijk` - America/Kralendijk
*   `America/La_Paz` - America/La\_Paz
*   `America/Lima` - America/Lima
*   `America/Los_Angeles` - America/Los\_Angeles
*   `America/Lower_Princes` - America/Lower\_Princes
*   `America/Maceio` - America/Maceio
*   `America/Managua` - America/Managua
*   `America/Manaus` - America/Manaus
*   `America/Marigot` - America/Marigot
*   `America/Martinique` - America/Martinique
*   `America/Matamoros` - America/Matamoros
*   `America/Mazatlan` - America/Mazatlan
*   `America/Menominee` - America/Menominee
*   `America/Merida` - America/Merida
*   `America/Metlakatla` - America/Metlakatla
*   `America/Mexico_City` - America/Mexico\_City
*   `America/Miquelon` - America/Miquelon
*   `America/Moncton` - America/Moncton
*   `America/Monterrey` - America/Monterrey
*   `America/Montevideo` - America/Montevideo
*   `America/Montserrat` - America/Montserrat
*   `America/Nassau` - America/Nassau
*   `America/New_York` - America/New\_York
*   `America/Nome` - America/Nome
*   `America/Noronha` - America/Noronha
*   `America/North_Dakota/Beulah` - America/North\_Dakota/Beulah
*   `America/North_Dakota/Center` - America/North\_Dakota/Center
*   `America/North_Dakota/New_Salem` - America/North\_Dakota/New\_Salem
*   `America/Nuuk` - America/Nuuk
*   `America/Ojinaga` - America/Ojinaga
*   `America/Panama` - America/Panama
*   `America/Paramaribo` - America/Paramaribo
*   `America/Phoenix` - America/Phoenix
*   `America/Port-au-Prince` - America/Port-au-Prince
*   `America/Port_of_Spain` - America/Port\_of\_Spain
*   `America/Porto_Velho` - America/Porto\_Velho
*   `America/Puerto_Rico` - America/Puerto\_Rico
*   `America/Punta_Arenas` - America/Punta\_Arenas
*   `America/Rankin_Inlet` - America/Rankin\_Inlet
*   `America/Recife` - America/Recife
*   `America/Regina` - America/Regina
*   `America/Resolute` - America/Resolute
*   `America/Rio_Branco` - America/Rio\_Branco
*   `America/Santarem` - America/Santarem
*   `America/Santiago` - America/Santiago
*   `America/Santo_Domingo` - America/Santo\_Domingo
*   `America/Sao_Paulo` - America/Sao\_Paulo
*   `America/Scoresbysund` - America/Scoresbysund
*   `America/Sitka` - America/Sitka
*   `America/St_Barthelemy` - America/St\_Barthelemy
*   `America/St_Johns` - America/St\_Johns
*   `America/St_Kitts` - America/St\_Kitts
*   `America/St_Lucia` - America/St\_Lucia
*   `America/St_Thomas` - America/St\_Thomas
*   `America/St_Vincent` - America/St\_Vincent
*   `America/Swift_Current` - America/Swift\_Current
*   `America/Tegucigalpa` - America/Tegucigalpa
*   `America/Thule` - America/Thule
*   `America/Tijuana` - America/Tijuana
*   `America/Toronto` - America/Toronto
*   `America/Tortola` - America/Tortola
*   `America/Vancouver` - America/Vancouver
*   `America/Whitehorse` - America/Whitehorse
*   `America/Winnipeg` - America/Winnipeg
*   `America/Yakutat` - America/Yakutat
*   `Antarctica/Casey` - Antarctica/Casey
*   `Antarctica/Davis` - Antarctica/Davis
*   `Antarctica/DumontDUrville` - Antarctica/DumontDUrville
*   `Antarctica/Macquarie` - Antarctica/Macquarie
*   `Antarctica/Mawson` - Antarctica/Mawson
*   `Antarctica/McMurdo` - Antarctica/McMurdo
*   `Antarctica/Palmer` - Antarctica/Palmer
*   `Antarctica/Rothera` - Antarctica/Rothera
*   `Antarctica/Syowa` - Antarctica/Syowa
*   `Antarctica/Troll` - Antarctica/Troll
*   `Antarctica/Vostok` - Antarctica/Vostok
*   `Arctic/Longyearbyen` - Arctic/Longyearbyen
*   `Asia/Aden` - Asia/Aden
*   `Asia/Almaty` - Asia/Almaty
*   `Asia/Amman` - Asia/Amman
*   `Asia/Anadyr` - Asia/Anadyr
*   `Asia/Aqtau` - Asia/Aqtau
*   `Asia/Aqtobe` - Asia/Aqtobe
*   `Asia/Ashgabat` - Asia/Ashgabat
*   `Asia/Atyrau` - Asia/Atyrau
*   `Asia/Baghdad` - Asia/Baghdad
*   `Asia/Bahrain` - Asia/Bahrain
*   `Asia/Baku` - Asia/Baku
*   `Asia/Bangkok` - Asia/Bangkok
*   `Asia/Barnaul` - Asia/Barnaul
*   `Asia/Beirut` - Asia/Beirut
*   `Asia/Bishkek` - Asia/Bishkek
*   `Asia/Brunei` - Asia/Brunei
*   `Asia/Chita` - Asia/Chita
*   `Asia/Choibalsan` - Asia/Choibalsan
*   `Asia/Colombo` - Asia/Colombo
*   `Asia/Damascus` - Asia/Damascus
*   `Asia/Dhaka` - Asia/Dhaka
*   `Asia/Dili` - Asia/Dili
*   `Asia/Dubai` - Asia/Dubai
*   `Asia/Dushanbe` - Asia/Dushanbe
*   `Asia/Famagusta` - Asia/Famagusta
*   `Asia/Gaza` - Asia/Gaza
*   `Asia/Hebron` - Asia/Hebron
*   `Asia/Ho_Chi_Minh` - Asia/Ho\_Chi\_Minh
*   `Asia/Hong_Kong` - Asia/Hong\_Kong
*   `Asia/Hovd` - Asia/Hovd
*   `Asia/Irkutsk` - Asia/Irkutsk
*   `Asia/Jakarta` - Asia/Jakarta
*   `Asia/Jayapura` - Asia/Jayapura
*   `Asia/Jerusalem` - Asia/Jerusalem
*   `Asia/Kabul` - Asia/Kabul
*   `Asia/Kamchatka` - Asia/Kamchatka
*   `Asia/Karachi` - Asia/Karachi
*   `Asia/Kathmandu` - Asia/Kathmandu
*   `Asia/Khandyga` - Asia/Khandyga
*   `Asia/Kolkata` - Asia/Kolkata
*   `Asia/Krasnoyarsk` - Asia/Krasnoyarsk
*   `Asia/Kuala_Lumpur` - Asia/Kuala\_Lumpur
*   `Asia/Kuching` - Asia/Kuching
*   `Asia/Kuwait` - Asia/Kuwait
*   `Asia/Macau` - Asia/Macau
*   `Asia/Magadan` - Asia/Magadan
*   `Asia/Makassar` - Asia/Makassar
*   `Asia/Manila` - Asia/Manila
*   `Asia/Muscat` - Asia/Muscat
*   `Asia/Nicosia` - Asia/Nicosia
*   `Asia/Novokuznetsk` - Asia/Novokuznetsk
*   `Asia/Novosibirsk` - Asia/Novosibirsk
*   `Asia/Omsk` - Asia/Omsk
*   `Asia/Oral` - Asia/Oral
*   `Asia/Phnom_Penh` - Asia/Phnom\_Penh
*   `Asia/Pontianak` - Asia/Pontianak
*   `Asia/Pyongyang` - Asia/Pyongyang
*   `Asia/Qatar` - Asia/Qatar
*   `Asia/Qostanay` - Asia/Qostanay
*   `Asia/Qyzylorda` - Asia/Qyzylorda
*   `Asia/Riyadh` - Asia/Riyadh
*   `Asia/Sakhalin` - Asia/Sakhalin
*   `Asia/Samarkand` - Asia/Samarkand
*   `Asia/Seoul` - Asia/Seoul
*   `Asia/Shanghai` - Asia/Shanghai
*   `Asia/Singapore` - Asia/Singapore
*   `Asia/Srednekolymsk` - Asia/Srednekolymsk
*   `Asia/Taipei` - Asia/Taipei
*   `Asia/Tashkent` - Asia/Tashkent
*   `Asia/Tbilisi` - Asia/Tbilisi
*   `Asia/Tehran` - Asia/Tehran
*   `Asia/Thimphu` - Asia/Thimphu
*   `Asia/Tokyo` - Asia/Tokyo
*   `Asia/Tomsk` - Asia/Tomsk
*   `Asia/Ulaanbaatar` - Asia/Ulaanbaatar
*   `Asia/Urumqi` - Asia/Urumqi
*   `Asia/Ust-Nera` - Asia/Ust-Nera
*   `Asia/Vientiane` - Asia/Vientiane
*   `Asia/Vladivostok` - Asia/Vladivostok
*   `Asia/Yakutsk` - Asia/Yakutsk
*   `Asia/Yangon` - Asia/Yangon
*   `Asia/Yekaterinburg` - Asia/Yekaterinburg
*   `Asia/Yerevan` - Asia/Yerevan
*   `Atlantic/Azores` - Atlantic/Azores
*   `Atlantic/Bermuda` - Atlantic/Bermuda
*   `Atlantic/Canary` - Atlantic/Canary
*   `Atlantic/Cape_Verde` - Atlantic/Cape\_Verde
*   `Atlantic/Faroe` - Atlantic/Faroe
*   `Atlantic/Madeira` - Atlantic/Madeira
*   `Atlantic/Reykjavik` - Atlantic/Reykjavik
*   `Atlantic/South_Georgia` - Atlantic/South\_Georgia
*   `Atlantic/St_Helena` - Atlantic/St\_Helena
*   `Atlantic/Stanley` - Atlantic/Stanley
*   `Australia/Adelaide` - Australia/Adelaide
*   `Australia/Brisbane` - Australia/Brisbane
*   `Australia/Broken_Hill` - Australia/Broken\_Hill
*   `Australia/Darwin` - Australia/Darwin
*   `Australia/Eucla` - Australia/Eucla
*   `Australia/Hobart` - Australia/Hobart
*   `Australia/Lindeman` - Australia/Lindeman
*   `Australia/Lord_Howe` - Australia/Lord\_Howe
*   `Australia/Melbourne` - Australia/Melbourne
*   `Australia/Perth` - Australia/Perth
*   `Australia/Sydney` - Australia/Sydney
*   `Canada/Atlantic` - Canada/Atlantic
*   `Canada/Central` - Canada/Central
*   `Canada/Eastern` - Canada/Eastern
*   `Canada/Mountain` - Canada/Mountain
*   `Canada/Newfoundland` - Canada/Newfoundland
*   `Canada/Pacific` - Canada/Pacific
*   `Europe/Amsterdam` - Europe/Amsterdam
*   `Europe/Andorra` - Europe/Andorra
*   `Europe/Astrakhan` - Europe/Astrakhan
*   `Europe/Athens` - Europe/Athens
*   `Europe/Belgrade` - Europe/Belgrade
*   `Europe/Berlin` - Europe/Berlin
*   `Europe/Bratislava` - Europe/Bratislava
*   `Europe/Brussels` - Europe/Brussels
*   `Europe/Bucharest` - Europe/Bucharest
*   `Europe/Budapest` - Europe/Budapest
*   `Europe/Busingen` - Europe/Busingen
*   `Europe/Chisinau` - Europe/Chisinau
*   `Europe/Copenhagen` - Europe/Copenhagen
*   `Europe/Dublin` - Europe/Dublin
*   `Europe/Gibraltar` - Europe/Gibraltar
*   `Europe/Guernsey` - Europe/Guernsey
*   `Europe/Helsinki` - Europe/Helsinki
*   `Europe/Isle_of_Man` - Europe/Isle\_of\_Man
*   `Europe/Istanbul` - Europe/Istanbul
*   `Europe/Jersey` - Europe/Jersey
*   `Europe/Kaliningrad` - Europe/Kaliningrad
*   `Europe/Kirov` - Europe/Kirov
*   `Europe/Kyiv` - Europe/Kyiv
*   `Europe/Lisbon` - Europe/Lisbon
*   `Europe/Ljubljana` - Europe/Ljubljana
*   `Europe/London` - Europe/London
*   `Europe/Luxembourg` - Europe/Luxembourg
*   `Europe/Madrid` - Europe/Madrid
*   `Europe/Malta` - Europe/Malta
*   `Europe/Mariehamn` - Europe/Mariehamn
*   `Europe/Minsk` - Europe/Minsk
*   `Europe/Monaco` - Europe/Monaco
*   `Europe/Moscow` - Europe/Moscow
*   `Europe/Oslo` - Europe/Oslo
*   `Europe/Paris` - Europe/Paris
*   `Europe/Podgorica` - Europe/Podgorica
*   `Europe/Prague` - Europe/Prague
*   `Europe/Riga` - Europe/Riga
*   `Europe/Rome` - Europe/Rome
*   `Europe/Samara` - Europe/Samara
*   `Europe/San_Marino` - Europe/San\_Marino
*   `Europe/Sarajevo` - Europe/Sarajevo
*   `Europe/Saratov` - Europe/Saratov
*   `Europe/Simferopol` - Europe/Simferopol
*   `Europe/Skopje` - Europe/Skopje
*   `Europe/Sofia` - Europe/Sofia
*   `Europe/Stockholm` - Europe/Stockholm
*   `Europe/Tallinn` - Europe/Tallinn
*   `Europe/Tirane` - Europe/Tirane
*   `Europe/Ulyanovsk` - Europe/Ulyanovsk
*   `Europe/Vaduz` - Europe/Vaduz
*   `Europe/Vatican` - Europe/Vatican
*   `Europe/Vienna` - Europe/Vienna
*   `Europe/Vilnius` - Europe/Vilnius
*   `Europe/Volgograd` - Europe/Volgograd
*   `Europe/Warsaw` - Europe/Warsaw
*   `Europe/Zagreb` - Europe/Zagreb
*   `Europe/Zurich` - Europe/Zurich
*   `GMT` - GMT
*   `Indian/Antananarivo` - Indian/Antananarivo
*   `Indian/Chagos` - Indian/Chagos
*   `Indian/Christmas` - Indian/Christmas
*   `Indian/Cocos` - Indian/Cocos
*   `Indian/Comoro` - Indian/Comoro
*   `Indian/Kerguelen` - Indian/Kerguelen
*   `Indian/Mahe` - Indian/Mahe
*   `Indian/Maldives` - Indian/Maldives
*   `Indian/Mauritius` - Indian/Mauritius
*   `Indian/Mayotte` - Indian/Mayotte
*   `Indian/Reunion` - Indian/Reunion
*   `Pacific/Apia` - Pacific/Apia
*   `Pacific/Auckland` - Pacific/Auckland
*   `Pacific/Bougainville` - Pacific/Bougainville
*   `Pacific/Chatham` - Pacific/Chatham
*   `Pacific/Chuuk` - Pacific/Chuuk
*   `Pacific/Easter` - Pacific/Easter
*   `Pacific/Efate` - Pacific/Efate
*   `Pacific/Fakaofo` - Pacific/Fakaofo
*   `Pacific/Fiji` - Pacific/Fiji
*   `Pacific/Funafuti` - Pacific/Funafuti
*   `Pacific/Galapagos` - Pacific/Galapagos
*   `Pacific/Gambier` - Pacific/Gambier
*   `Pacific/Guadalcanal` - Pacific/Guadalcanal
*   `Pacific/Guam` - Pacific/Guam
*   `Pacific/Honolulu` - Pacific/Honolulu
*   `Pacific/Kanton` - Pacific/Kanton
*   `Pacific/Kiritimati` - Pacific/Kiritimati
*   `Pacific/Kosrae` - Pacific/Kosrae
*   `Pacific/Kwajalein` - Pacific/Kwajalein
*   `Pacific/Majuro` - Pacific/Majuro
*   `Pacific/Marquesas` - Pacific/Marquesas
*   `Pacific/Midway` - Pacific/Midway
*   `Pacific/Nauru` - Pacific/Nauru
*   `Pacific/Niue` - Pacific/Niue
*   `Pacific/Norfolk` - Pacific/Norfolk
*   `Pacific/Noumea` - Pacific/Noumea
*   `Pacific/Pago_Pago` - Pacific/Pago\_Pago
*   `Pacific/Palau` - Pacific/Palau
*   `Pacific/Pitcairn` - Pacific/Pitcairn
*   `Pacific/Pohnpei` - Pacific/Pohnpei
*   `Pacific/Port_Moresby` - Pacific/Port\_Moresby
*   `Pacific/Rarotonga` - Pacific/Rarotonga
*   `Pacific/Saipan` - Pacific/Saipan
*   `Pacific/Tahiti` - Pacific/Tahiti
*   `Pacific/Tarawa` - Pacific/Tarawa
*   `Pacific/Tongatapu` - Pacific/Tongatapu
*   `Pacific/Wake` - Pacific/Wake
*   `Pacific/Wallis` - Pacific/Wallis
*   `US/Alaska` - US/Alaska
*   `US/Arizona` - US/Arizona
*   `US/Central` - US/Central
*   `US/Eastern` - US/Eastern
*   `US/Hawaii` - US/Hawaii
*   `US/Mountain` - US/Mountain
*   `US/Pacific` - US/Pacific
*   `UTC` - UTC

`external_source`:optionalstring

External source.

`external_id`:optionalstring

External id.

`is_issue_type_enabled`:optionalboolean

Is issue type enabled.

`is_time_tracking_enabled`:optionalboolean

Is time tracking enabled.



```bash
curl -X POST \
  "https://api.plane.so/api/v1/workspaces/my-workspace/projects/" \
  -H "X-API-Key: $PLANE_API_KEY" \
  # Or use -H "Authorization: Bearer $PLANE_OAUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Example Name",
  "description": "Example description",
  "identifier": "PROJ-123",
  "project_lead": "550e8400-e29b-41d4-a716-446655440000"
}'
```




```python
import requests

response = requests.post(
    "https://api.plane.so/api/v1/workspaces/my-workspace/projects/",
    headers={"X-API-Key": "your-api-key"},
    json={
      "name": "Example Name",
      "description": "Example description",
      "identifier": "PROJ-123",
      "project_lead": "550e8400-e29b-41d4-a716-446655440000"
    }
)
print(response.json())
```



```javascript
const response = await fetch("https://api.plane.so/api/v1/workspaces/my-workspace/projects/", {
  method: "POST",
  headers: {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    name: "Example Name",
    description: "Example description",
    identifier: "PROJ-123",
    project_lead: "550e8400-e29b-41d4-a716-446655440000",
  }),
});
const data = await response.json();
```



```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Example Name",
  "description": "Example description",
  "identifier": "PROJ-123",
  "network": 2,
  "project_lead": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```
