import { Carousel } from "flowbite";
import { format, setDefaultOptions } from "date-fns";
import { ru } from 'date-fns/locale';

setDefaultOptions({ locale: ru });

const carouselElement = document.getElementById('carousel-example');

const items = [
    {
        position: 0,
        el: document.getElementById('carousel-item-1'),
    },
    {
        position: 1,
        el: document.getElementById('carousel-item-2'),
    },
    {
        position: 2,
        el: document.getElementById('carousel-item-3'),
    },
    {
        position: 3,
        el: document.getElementById('carousel-item-4'),
    },
];

// options with default values
const options = {
    defaultPosition: 0,
    interval: 3000,

    indicators: {
        activeClasses: 'bg-main',
        inactiveClasses:
            'bg-slate-500 hover:bg-main/50',
        items: [
            {
                position: 0,
                el: document.getElementById('carousel-indicator-1'),
            },
            {
                position: 1,
                el: document.getElementById('carousel-indicator-2'),
            },
            {
                position: 2,
                el: document.getElementById('carousel-indicator-3'),
            },
            {
                position: 3,
                el: document.getElementById('carousel-indicator-4'),
            },
        ],
    },

    // callback functions
    onNext: () => {
        console.log('next slider item is shown');
    },
    onPrev: () => {
        console.log('previous slider item is shown');
    },
    onChange: () => {
        console.log('new slider item has been shown');
    },
};

// instance options object
const instanceOptions = {
  id: 'carousel-example',
  override: true
};

const carousel = new Carousel(carouselElement, items, options, instanceOptions);

carousel.cycle();

const dates = document.querySelectorAll('#date');

dates.forEach((date) =>{
    date.innerHTML = format(new Date(Number(date.dataset.time)*1000), "k:m");
});

const imagesNodes = document.querySelectorAll('[data-type="image"]');
imagesNodes.forEach((item) => {
    let previosSibling = item.previousElementSibling;
    if (previosSibling !== null) previosSibling.classList.add("hidden");
});

