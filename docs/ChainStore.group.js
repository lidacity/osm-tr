Group =
{
 green: L.layerGroup([], {title: 'Всё в порядке', short: 'Ok', icon: new LeafIcon({iconUrl: './img/marker-icon-green.png'}), }),
 blue: L.layerGroup([], {title: 'Заполнены не все тэги', short: 'Тэги', icon: new LeafIcon({iconUrl: './img/marker-icon-blue.png'}), }),
 violet: L.layerGroup([], {title: 'Заполнены не все тэги (ТР)', short: 'Тэги ТР', icon: new LeafIcon({iconUrl: './img/marker-icon-violet.png'}), }),
 red: L.layerGroup([], {title: 'Есть в сети, но нет на карте', short: 'Отсутстует', icon: new LeafIcon({iconUrl: './img/marker-icon-red.png'}), }),
 black: L.layerGroup([], {title: 'Нет в сети, но есть на карте', short: 'Лишний', icon: new LeafIcon({iconUrl: './img/marker-icon-black.png'}), }),
};
