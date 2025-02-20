document.addEventListener('DOMContentLoaded', function() {
    const restaurantSelect = document.querySelector('#id_restaurant');
    if (!restaurantSelect) return;

    // Initialize elements with null checks
    const menuCategorySelect = document.querySelector('#id_menu_category');
    const hasMultiplePricesCheckbox = document.querySelector('#id_has_multiple_prices');
    const priceInline = document.querySelector('.dynamic-menuitemprice_set');
    let currentDesignData = null;

    async function loadMenuDesign(restaurantId) {
        try {
            const designResponse = await fetch(`/api/menus/menu-designs/${restaurantId}/`);
            
            if (!designResponse.ok) {
                if (designResponse.status === 404) {
                    console.warn('No menu design found');
                    resetFormFields();
                    return;
                }
                throw new Error(`HTTP error! status: ${designResponse.status}`);
            }

            currentDesignData = await designResponse.json();
            
            // Update category dropdown
            if (menuCategorySelect) {
                menuCategorySelect.innerHTML = '<option value="">---------</option>';
                currentDesignData.categories.forEach(category => {
                    const option = new Option(category.name, category.id);
                    menuCategorySelect.add(option);
                });
            }

            // Update pricing controls
            updatePricingControls();

        } catch (error) {
            console.error('Error loading menu design:', error);
            resetFormFields();
        }
    }

    function updatePricingControls() {
        if (!currentDesignData) return;

        // Remove checkbox completely
        const checkboxRow = document.querySelector('.field-has_multiple_prices');
        if (checkboxRow) {
            checkboxRow.style.display = 'none';
        }

        // Handle price inline section
        if (priceInline) {
            // Remove existing message if it exists
            const existingMessage = priceInline.querySelector('.pricing-message');
            if (existingMessage) {
                existingMessage.remove();
            }

            // Add message if multiple pricing is enabled
            if (currentDesignData.is_multiple_pricing) {
                const message = document.createElement('div');
                message.className = 'pricing-message';
                message.innerHTML = `
                    <div style="padding: 10px; background: #f0f8ff; border-left: 4px solid #2196F3; margin-bottom: 15px;">
                        <strong>This Restaurant uses multiple pricing</strong><br>
                        Please set prices for each pricing title configured in the menu design.
                    </div>
                `;
                priceInline.insertBefore(message, priceInline.firstChild);
            }

            // Always show pricing section when menu design exists
            priceInline.style.display = 'block';
            
            // Update all existing pricing title selects
            const pricingSelects = priceInline.querySelectorAll('select[id$="-pricing_title"]');
            pricingSelects.forEach(select => {
                select.innerHTML = '<option value="">---------</option>';
                currentDesignData.pricing_titles.forEach(title => {
                    const option = new Option(title.name, title.id);
                    select.add(option);
                });
            });
        }
    }

    // Helper functions
    function resetFormFields() {
        currentDesignData = null;
        if (hasMultiplePricesCheckbox) {
            hasMultiplePricesCheckbox.checked = false;
            hasMultiplePricesCheckbox.disabled = false;
            hasMultiplePricesCheckbox.closest('.form-row').style.display = 'block';
        }
        if (priceInline) priceInline.style.display = 'none';
        if (menuCategorySelect) {
            menuCategorySelect.innerHTML = '<option value="">No menu design configured</option>';
        }
    }

    // Handle dynamically added inline items
    document.addEventListener('formset:added', (event) => {
        if (event.detail.prefix === 'prices' && currentDesignData) {
            const newRow = event.detail.row;
            const pricingSelect = newRow.querySelector('select[id$="-pricing_title"]');
            
            if (pricingSelect) {
                pricingSelect.innerHTML = '<option value="">---------</option>';
                currentDesignData.pricing_titles.forEach(title => {
                    const option = new Option(title.name, title.id);
                    pricingSelect.add(option);
                });
            }
        }
    });

    // Initial load
    if (restaurantSelect.value) {
        loadMenuDesign(restaurantSelect.value);
    }

    // Handle restaurant changes
    restaurantSelect.addEventListener('change', function() {
        if (this.value) {
            loadMenuDesign(this.value);
        } else {
            resetFormFields();
        }
    });
}); 