function Popup(Feature, Layer)
{
 var Properties = Feature['properties'];
 var Result = '';
 //
 var Content = new Array();
 if (Properties['name:be'])
  Content.push(`<h3>${Properties['name:be']}</h3>`);
 if (Properties['name:ru'])
  Content.push(`<div class="popup-field"><strong>Название</strong>: ${Properties['name:ru']}</div>`);
 if (Properties['addr:full'])
  Content.push(`<div class="popup-field"><strong>Адрес</strong>: ${Properties['addr:full']}</div>`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
 Content = new Array();
 if (Properties['shop'])
  Content.push(`<div class="popup-field"><strong>Тип магазина</strong>: ${Properties['shop']}</div>`);
 if (Properties['ref'])
  Content.push(`<div class="popup-field"><strong>Идентификатор</strong>: ${Properties['ref']}</div>`);
 if (Properties['brand'])
  Content.push(`<div class="popup-field"><strong>Брэнд</strong>: ${Properties['brand']}</div>`);
 if (Properties['operator:wikidata'])
  Content.push(`<div class="popup-field"><strong>Вики</strong>: <a target="_blank" href="https://wikidata.org/wiki/${Properties['operator:wikidata']}/">${Properties['operator:wikidata']}</a></div>`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
 //
 Content = new Array();
 if (Properties['operator:ref:BY:PAN'])
  Content.push(`<div class="popup-field"><strong>УНП</strong>: <a target="_blank" href="https://etalonline.by/egr-status/${Properties['operator:ref:BY:PAN']}/">${Properties['operator:ref:BY:PAN']}</a></div>`);
 if (Properties['ref:BY:trade_register'])
  Content.push(`<div class="popup-field"><strong>Номер в торговом реестре</strong>: <a href="?ID=${Properties['ref:BY:trade_register']}">${Properties['ref:BY:trade_register']}</a></div>`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
 //
 if (Properties['status'] != "green")
 {
  Result += `
   <div class="popup-content">
    <div class="popup-field">ref:BY:trade_register=${Properties['ref:BY:trade_register']} &nbsp; <button id="clipboard" onclick="Clipboard('ref:BY:trade_register=${Properties['ref:BY:trade_register']}');">копировать</button></div>
   </div>
   <hr />`;
 }
 //
 Content = new Array();
 var Lat = Feature.geometry.coordinates[1];
 var Lon = Feature.geometry.coordinates[0];
 var FullID = Properties['ID'];
 if (FullID)
 {
  var ShortType = Array.from(FullID)[0];
  var ID = FullID.substring(1);
  var Type = '';
  if (ShortType == 'n')
   Type = 'node';
  if (ShortType == 'w')
   Type = 'way';
  Content.push(`<a target="_blank" href="https://openstreetmap.org/${Type}/${ID}">osm</a>`);
  Content.push(`<a target="_josm" href="http://localhost:8111/load_object?objects=${FullID}&relation_members=true&referrers=true" onclick='return LoadObject("${FullID}");'>josm</a>`);
  Content.push(`<a target="_id" href="https://www.openstreetmap.org/edit?${ShortType}=${ID}#map=19/${Lat}/${Lon}");'>iD</a>`);
  Content.push(`<a target="_blank" href="https://pewu.github.io/osm-history/#/${Type}/${ID}">history</a>`);
  Content.push(`<a target="_blank" href="https://mapillary.com/app/?lat=${Lat}&lng=${Lon}&z=18">Mapillary</a>`);
 }
 else if (["orange", "red"].includes(Properties['status']))
 {
  Content.push(`<a target="_blank" href="https://openstreetmap.org/#map=17/${Lat}/${Lon}" target="_blank">osm</a>`);
  Content.push(`<a target="_josm" href="http://localhost:8111/load_and_zoom?left=${Lon}&top=${Lat}&right=${Lon}&bottom=${Lat}" onclick='return LoadAndZoom(${Lat}, ${Lon});'>josm</a>`);
  Content.push(`<a target="_blank" href="https://mapillary.com/app/?lat=${Lat}&lng=${Lon}&z=18">Mapillary</a>`);
 }
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    <div class="popup-field">${Content.join('&nbsp;&nbsp;')}</div>
   </div>`;
 //
 Layer.bindPopup(Result);
}


DateLegend =
{
 Trade: "Дата торгового реестра",
 Update: "Дата обновления",
};

