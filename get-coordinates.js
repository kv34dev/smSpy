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

// dont consent cookies
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
