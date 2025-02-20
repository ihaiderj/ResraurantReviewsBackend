document.addEventListener('DOMContentLoaded', function() {
    const multiPricingCheckbox = document.querySelector('#id_is_multiple_pricing');
    const form = multiPricingCheckbox?.closest('form');
    
    if (multiPricingCheckbox && form) {
        // Handle checkbox change
        multiPricingCheckbox.addEventListener('change', function() {
            // Add the checkbox state to the URL and reload
            const url = new URL(window.location);
            url.searchParams.set('is_multiple_pricing', this.checked ? 'on' : '');
            window.location = url.toString();
        });
        
        // Handle form submission
        form.addEventListener('submit', function(e) {
            if (!multiPricingCheckbox.checked) {
                // Remove any pricing data if multiple pricing is disabled
                const pricingInputs = form.querySelectorAll('.dynamic-menudesignpricing_set input, .dynamic-menudesignpricing_set select');
                pricingInputs.forEach(input => input.disabled = true);
            }
        });
    }
}); 