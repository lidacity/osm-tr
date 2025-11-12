var OptionIcon =
{
 iconSize: [25, 41],
 iconAnchor: [12, 41],
 popupAnchor: [1, -34],
};

var LeafIcon = L.Icon.extend({options: OptionIcon});

var Group =
{
 green: L.layerGroup([], {title: 'Всё в порядке', short: 'Ok', icon: new LeafIcon({iconUrl: './img/marker-icon-green.png'}), }),
 blue: L.layerGroup([], {title: 'Совпадение имени', short: 'Имя', icon: new LeafIcon({iconUrl: './img/marker-icon-blue.png'}), }),
 violet: L.layerGroup([], {title: 'Совпадение места', short: 'Место', icon: new LeafIcon({iconUrl: './img/marker-icon-violet.png'}), }),
 orange: L.layerGroup([], {title: 'Совпадение адреса', short: 'Адрес', icon: new LeafIcon({iconUrl: './img/marker-icon-orange.png'}), }),
 gold: L.layerGroup([], {title: 'Повторы', short: 'Дубли', icon: new LeafIcon({iconUrl: './img/marker-icon-gold.png'}), }),
 grey: L.layerGroup([], {title: 'В процессе ликвидации', short: 'Ликвидация', icon: new LeafIcon({iconUrl: './img/marker-icon-grey.png'}), }),
 black: L.layerGroup([], {title: 'Нет в реестре, но есть на карте', short: 'Ошибка', icon: new LeafIcon({iconUrl: './img/marker-icon-black.png'}), }),
 red: L.layerGroup([], {title: 'Не найден', short: 'Отсутстует', icon: new LeafIcon({iconUrl: './img/marker-icon-red.png'}), }),
};
