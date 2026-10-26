/**
 * Currency formatting utility supporting Indian Lakh/Crore systems and international conventions.
 */

const CURRENCY_SYMBOLS = {
  INR: "₹",
  USD: "$",
  EUR: "€",
  GBP: "£",
  AED: "AED ",
  CAD: "CA$",
  AUD: "AU$",
  SGD: "SG$"
};

export function getCurrencySymbol(currencyCode = "INR") {
  return CURRENCY_SYMBOLS[currencyCode.toUpperCase()] || `${currencyCode.toUpperCase()} `;
}

export function formatCurrency(amount, currencyCode = "INR") {
  if (amount === undefined || amount === null || isNaN(amount)) return "0.00";
  
  const num = Number(amount);
  const symbol = getCurrencySymbol(currencyCode);

  if (currencyCode.toUpperCase() === "INR") {
    // Format using Indian Numbering System (e.g. 1,50,000)
    return `${symbol}${num.toLocaleString("en-IN", {
      maximumFractionDigits: 0
    })}`;
  }

  return `${symbol}${num.toLocaleString("en-US", {
    maximumFractionDigits: 0
  })}`;
}
