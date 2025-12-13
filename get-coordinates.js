// for ig

// input form
const element = document.querySelector('input.search.search-form__input');

if (element) {
    const rect = element.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

    const absoluteTop = rect.top + scrollTop;
    const absoluteLeft = rect.left + scrollLeft;

    console.log('Coordinates relative to the viewport:', rect.top, rect.left);
    console.log('Coordinates relative to the page:', absoluteTop, absoluteLeft);
} else {
    console.log('Element not found!');
}

// n cookies
const element = document.querySelector('p.fc-button-label');

if (element) {
    const rect = element.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

    const absoluteTop = rect.top + scrollTop;
    const absoluteLeft = rect.left + scrollLeft;

    console.log('Coordinates relative to the viewport:', rect.top, rect.left);
    console.log('Coordinates relative to the page:', absoluteTop, absoluteLeft);
} else {
    console.log('Element not found!');
}


// for tiktok

// n capcha
const element = document.querySelector('#captcha_close_button');

if (element) {
    const rect = element.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

    const absoluteTop = rect.top + scrollTop;
    const absoluteLeft = rect.left + scrollLeft;

    console.log('Coordinates relative to the viewport:', rect.top, rect.left);
    console.log('Coordinates relative to the page:', absoluteTop, absoluteLeft);
} else {
    console.log('Button not found!');
}

// avatar
const element = document.querySelector('[data-e2e="user-avatar"]');

if (element) {
    const rect = element.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

    const absoluteTop = rect.top + scrollTop;
    const absoluteLeft = rect.left + scrollLeft;

    console.log('Coordinates relative to the viewport:', rect.top, rect.left);
    console.log('Coordinates relative to the page:', absoluteTop, absoluteLeft);

    // Optional: center of the avatar
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    console.log('Center:', centerX, centerY);
} else {
    console.log('Avatar not found!');
}

