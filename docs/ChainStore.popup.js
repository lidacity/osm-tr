function Popup(Feature, Layer)
{
 var Properties = Feature.properties;
 var Result = '';
 var Tag = "";
 //
 var Content = new Array();
 if (Tag = Properties['name:be'])
  Content.push(`<h3>${Tag}</h3>`);
 if (Tag = Properties['shop'])
  Content.push(`<div class="popup-field"><strong>Тип магазина</strong>: ${Tag}</div>`);
 if (Tag = Properties['ref'])
  Content.push(`<div class="popup-field"><strong>Идентификатор</strong>: ${Tag}</div>`);
 if (Tag = Properties['addr:full'])
  Content.push(`<div class="popup-field"><strong>Адрес</strong>: ${Tag}</div>`);
 if (Tag = Properties['opening_hours'])
  Content.push(`<div class="popup-field"><strong>Время работы</strong>: ${Tag}</div>`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
 //
 Content = new Array();

 if (Tag = Properties['name:ru'])
  Content.push(`<div class="popup-field"><strong>Название</strong>: ${Tag}</div>`);
 if (Tag = Properties['brand'])
 {
  const Wikidata = Properties['brand:wikidata']
  Content.push(`<div class="popup-field"><strong>Брэнд</strong>: ${Tag} (<a target="_blank" href="https://wikidata.org/wiki/${Wikidata}/">${Wikidata}</a>)</div>`);
 }
 if (Tag = Properties['operator'])
 {
  const Wikidata = Properties['operator:wikidata']
  Content.push(`<div class="popup-field"><strong>Оператор</strong>: ${Tag} (<a target="_blank" href="https://wikidata.org/wiki/${Wikidata}/">${Wikidata}</a>)</div>`);
 }
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
 //
 Content = new Array();
 if (Tag = Properties['ref:vatin'])
 {
  Content.push(`<div class="popup-field"><strong>УНП</strong>: <a target="_blank" href="https://etalonline.by/egr-status/${Tag}/">${Tag}</a></div>`);
  Properties['ref:vatin'] = `BY${Tag}`;
 }
 if (Tag = Properties['ref:BY:trade_register'])
  Content.push(`<div class="popup-field"><strong>Номер в торговом реестре</strong>: <a href="?ID=${Tag}">${Tag}</a></div>`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
 //
 if (Properties['status'] != "green")
 {
  Content = new Array();
  const Keys = ['shop', 'operator', 'operator:wikidata', 'brand', 'brand:wikidata', 'ref:vatin', 'name', 'name:be', 'name:ru', 'ref:BY:trade_register', 'ref', 'ref:shop'];
  var Temp = GetClipboardText(Properties, Keys);
  if (Temp.length > 0)
  {
   Text = Temp.join("<br />");
   Clip = encodeURIComponent(Temp.join("\\n"))
   Content.push(`<div class="popup-field">${Text}<br /><button id="clipboard" onclick="Clipboard('${Clip}');">копировать</button></div>`);
   if (Content.length > 0)
    Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
  }
 }
 //
 Content = new Array();
 var Lat = Feature.geometry.coordinates[1];
 var Lon = Feature.geometry.coordinates[0];
 var FullID = Feature.id;
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
 Update: "Дата обновления",
};

