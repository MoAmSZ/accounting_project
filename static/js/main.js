// تابع فرمت‌کردن اعداد به فرمت پول
function formatMoney(amount) {
    return new Intl.NumberFormat('fa-IR').format(amount);
}

// تابع تبدیل اعداد انگلیسی به فارسی
function toFarsiNumber(n) {
    const farsiDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return n.toString().replace(/\d/g, x => farsiDigits[x]);
}

// تابع آپدیت خودکار مبالغ به فرمت پول
document.addEventListener('DOMContentLoaded', function() {
    const moneyElements = document.querySelectorAll('.money-format');
    moneyElements.forEach(element => {
        const amount = element.textContent;
        element.textContent = formatMoney(amount);
    });
});

// تابع نمایش تأییدیه حذف
function confirmDelete(event, message) {
    if (!confirm(message || 'آیا از حذف این مورد اطمینان دارید؟')) {
        event.preventDefault();
    }
}

// تابع محاسبه درصد پیشرفت
function calculateProgress(current, target) {
    return Math.min(Math.round((current / target) * 100), 100);
}

// تابع به‌روزرسانی نوارهای پیشرفت
function updateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const current = parseFloat(bar.getAttribute('data-current'));
        const target = parseFloat(bar.getAttribute('data-target'));
        const progress = calculateProgress(current, target);
        bar.style.width = `${progress}%`;
        bar.setAttribute('aria-valuenow', progress);
        bar.textContent = `${toFarsiNumber(progress)}%`;
    });
}

// اجرای توابع اولیه بعد از بارگذاری صفحه
document.addEventListener('DOMContentLoaded', function() {
    updateProgressBars();
}); 