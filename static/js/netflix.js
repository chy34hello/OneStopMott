#!/usr/bin/env node

const fs = require('fs');
const XLSX = require('xlsx');
const XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
const country_code = process.env.COUNTRY_CODE;

const romanToDecimal = {
    M: 1000,
    CM: 900,
    D: 500,
    CD: 400,
    C: 100,
    XC: 90,
    L: 50,
    XL: 40,
    X: 10,
    IX: 9,
    V: 5,
    IV: 4,
    I: 1
};

function romanToDec(roman) {
    let result = 0;
    for (let i = 0; i < roman.length; i++) {
        const currentChar = roman[i];
        const nextChar = roman[i + 1];
        const currentValue = romanToDecimal[currentChar];
        const nextValue = romanToDecimal[nextChar];
        if (nextValue > currentValue) {
            result -= currentValue;
        } else {
            result += currentValue;
        }
    }
    return result;
}

function fetchNetflixData() {
    const url = "https://www.netflix.com/au/browse/genre/839338";
    const language = "en-EN";
    const req = new XMLHttpRequest();
    req.open('GET', url, false);
    req.setRequestHeader("Accept-Language", language);
    req.send(null);
    if (req.status == 200) {
        const data = req.responseText;
        const regex = /^.*"itemListElement":/;
        const startIndex = data.search(regex) + regex.exec(data)[0].length;
        const endIndex = data.indexOf("}</script>", startIndex);
        const jsonData = data.substring(startIndex, endIndex);
        const list = JSON.parse(jsonData);
        const titles = list.map(item => item.item.name);
        return titles;
    } else {
        throw new Error(`Failed to fetch Netflix data: HTTP status code ${req.status}`);
    }
}

function processNetflixData(titles) {
    const videoTitles = titles.map(title => title.replace(/&/g, "and").replace(/Rome ([IVXLCDM]+)/g, (match, romanNumeral) => romanToDec(romanNumeral)));
    return videoTitles;
}

function generateExcelFile(videoTitles) {
    const workbook = XLSX.utils.book_new();
    const worksheet = XLSX.utils.json_to_sheet([{ "No.": "Number", "Video Title": "Title", "Utterances": "Utterance" }], { header: ["No.", "Video Title", "Utterances"], skipHeader: true });
    worksheet['!cols'] = [{ width: 5 }, { width: 30 }, { width: 50 }];

    videoTitles.forEach((title, index) => {
        const rowNumber = index + 1;
        const utterance = `play ${title} from netflix`;
        const row = { "No.": rowNumber, "Video Title": title, "Utterances": utterance };
        XLSX.utils.sheet_add_json(worksheet, [row], { skipHeader: true, origin: -1 });
    });

    const range = XLSX.utils.decode_range(worksheet['!ref']);
    worksheet['!autofilter'] = { ref: XLSX.utils.encode_range(range) };
    XLSX.utils.book_append_sheet(workbook, worksheet, "Sheet1");
    XLSX.writeFile(workbook, "netflix.xlsx");
}

function main() {
    try {
        const titles = fetchNetflixData();
        const videoTitles = processNetflixData(titles);
        generateExcelFile(videoTitles);
        console.log("Excel file created successfully.");
    } catch (error) {
        console.error(error);
    }
}

main();
