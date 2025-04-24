document.addEventListener('DOMContentLoaded', function () {

        // Filter functionality
        const filterInputs = document.querySelectorAll('.filter-input');
    
        function applyFilters() {
            const tables = document.querySelectorAll('.table');
            
            tables.forEach(tableElement => {
                const tableId = tableElement.closest('.tab-pane').id;
                const rows = tableElement.querySelectorAll('tbody tr');
                
                // Get all filters for this table
                const tableFilters = {};
                const allowedFilters = ['Haras', 'Name', 'Sire', 'Dam', 'Href', 'Sex']; // Only allow these filters
                
                document.querySelectorAll(`#${tableId} .filter-input`).forEach(input => {
                    const column = input.dataset.column;
                    if (allowedFilters.includes(column)) { // Only process allowed filters
                        const value = input.value.toLowerCase();
                        if (value) {
                            tableFilters[column] = value;
                        }
                    }
                });
                
                // Apply all filters to each row
                rows.forEach(row => {
                    let shouldShow = true;
                    
                    for (const [column, value] of Object.entries(tableFilters)) {
                        const cell = row.querySelector(`td:nth-child(${getColumnIndex(tableElement, column)})`);
                        if (cell) {
                            const cellText = cell.textContent.toLowerCase();
                            if (!cellText.includes(value)) {
                                shouldShow = false;
                                break;
                            }
                        }
                    }
                    
                    row.style.display = shouldShow ? '' : 'none';
                });
            });
        }
        
        // Add input event listener to all filter inputs
        filterInputs.forEach(input => {
            input.addEventListener('input', applyFilters);
        });
    
        function getColumnIndex(table, columnName) {
            const headerRows = table.querySelectorAll('thead tr');
            if (headerRows.length < 3) return 0;
        
            const headers = headerRows[2].querySelectorAll('th');  // was [1]
            for (let i = 0; i < headers.length; i++) {
                if (headers[i].textContent.trim() === columnName) {
                    return i + 1;
                }
            }
            return 0;
        }
        function getColumnHeaders(table) {
            const headerRows = table.querySelectorAll('thead tr');
            return headerRows.length >= 3 ? headerRows[2].querySelectorAll('th') : [];
        }
     
    const columnConfig = {
        'PRS': { type: 'percentage' },
        'PR': { type: 'percentage' },
        'PS': { type: 'percentage' },
        'PB': { type: 'percentage' },
        'PBRS': { type: 'percentage' },
        'Inbreeding Coef.': { type: 'percentage' },
        'Start': { type: 'date' },
        'End': { type: 'date' },
        'Lote':{type: 'number'},
        'Price per Bp':{type: 'number'},
        'Auction Order':{type: 'number'}
    };

    const gradientColumns = ['PR', 'PS', 'PRS', 'PB', 'PBRS','Inbreeding Coef.'];
    const sortableColumns = Object.keys(columnConfig);
    const tables = document.querySelectorAll('.table');

    const group1Columns = ['STK Wnrs / Rnrs', 
                            '#RUnners/ Born at 3yo',
                            'Dam Stk Wnrs / RA Offs', 
                            'Dams RA Offs', 
                            'Dam Top 3 BSN\'s', 
                            'Dam\'s Foals Top 3 BSN',
                            'Dam Placed STK?',
                            'Dam Raced STK?',
                            'Dam Total Races',
                            'Dam\'s Foal Raced Stk?',
                            'Dam\'s Foal Placed Stk?',
                            'Dam\'s Siblings Total G1/G2',
                            'Dam\'s Siblings G1G2/Races',
                            'CEI per foal',
                            'Age'

                        ];
    const group2Columns = [
                            'Own Chars',
                            'Father',
                            'Father\'s Offs',
                            'Dam\'s Age and Racing Career',
                            'Dam\'s Offs',
                            'Dam\'s Sibs',
                            'Dam\'s Parents Career'
    ];
    const group3Columns = [
                            'Inbreeding',
                            'Dam\'s Season'
    ];
    const group1Columns_dams = [
        'Dam\'s Age and Racing Career',
        'Dam\'s Offs',
        'Dam\'s Sibs',
        'Dam\'s Parents Career'
    ];
    const group2Columns_dams = [
        'Dam\'s Season', 
        'Birth Rate (All)', 
        'Birth Rate (last 3)', 
        'Had Rest Year'
    
    ];
    const group3Columns_dams = [
        'Dam\'s total races',
        'Dam\'s total wins',
        'Dam\'s CEI',
        'Dam STK races',
        'Dam STK wins',
        'Dam G1 STK placed',
        'Dam G1 STK wins'
    ];
    const group4Columns_dams = [
        'Dam\'s Age', 
        // 'Dam Stk Wnrs / RA Offs', 
        'Dams RA Offs', 
        '#Offs Ran',
        'Dam Top 3 BSN\'s', 
        'Dam\'s Foals Top 3 BSN',
        'Dam Raced STK?',
        'Dam Total Races',
        'Dam\'s Foal Raced Stk?',
        'Dam\'s Foal Placed Stk?',
        'Dam\'s Siblings Total G1/G2',
        'Dam\'s Siblings G1G2/Races'
    ];
    
    const group1Columns_auctioned_horses = [
            'Value',
            'Value USDB',
            'Price per Bp',
            'Title',
            'Auction Order',
            'Year',
            'Auction Date'
    ]

    function parseValue(value, type) {
        if (!value || value === '-') return null;

        switch (type) {
            case 'date':
                const [day, month, year] = value.split('/');
                if (day && month && year) {
                    const fullYear = year.length === 2 ? `20${year}` : year;
                    return new Date(`${fullYear}-${month}-${day}`).getTime();
                }
                return null;
            case 'percentage':
                return parseFloat(value.replace('%', '')) || null;
            case 'number':
                return parseFloat(value) || null;
            case 'text':
            default:
                return value.toLowerCase();
        }
    }

    function compareValues(a, b, type, direction) {
        if (a === null && b === null) return 0;
        if (a === null) return 1;
        if (b === null) return -1;

        let comparison = 0;
        if (type === 'text') {
            comparison = a.localeCompare(b);
        } else {
            comparison = a - b;
        }

        return direction === 'asc' ? comparison : -comparison;
    }

    function applyGradientHighlighting() {
        tables.forEach(table => {
            const headers = getColumnHeaders(table);
            const isHorsesTable = table.closest('#horses') !== null;
            const maxValues = isHorsesTable ? horsesMaxValues : damsMaxValues;

            headers.forEach((header, index) => {
                const columnName = header.getAttribute('data-column');
                if (gradientColumns.includes(columnName)) {
                    const rows = table.querySelectorAll('tbody tr:not([style*="display: none"])');
                    const maxValue = maxValues[columnName];

                    rows.forEach(row => {
                        const cell = row.children[index];
                        const raw = cell.textContent.replace('%', '').trim();
                        const value = parseFloat(raw);

                        if (!isNaN(value) && maxValue > 0) {
                            let ratio;
                            if (columnName === 'Inbreeding Coef.') {
                                const minValue = 0;
                                ratio = 1 - (value - minValue) / (maxValue - minValue);
                            } else {
                                ratio = value / maxValue;
                            }
                            ratio = Math.max(0, Math.min(1, ratio));
                            const r = Math.floor(255 * (1 - ratio));
                            const g = Math.floor(255 * ratio);
                            const b = 0;
                            const alpha = 0.15 + ratio * 0.35;

                            cell.style.backgroundImage = `linear-gradient(rgba(${r}, ${g}, ${b}, ${alpha}), rgba(${r}, ${g}, ${b}, ${alpha}))`;
                            cell.style.backgroundColor = '';
                            cell.classList.add('gradient-cell');
                        } else {
                            cell.style.backgroundImage = '';
                            cell.style.backgroundColor = '';
                        }
                    });
                }
            });
        });
    }

    function applyColumnHighlighting() {
        tables.forEach(table => {
            const headers = getColumnHeaders(table);
            const rows = table.querySelectorAll('tbody tr');
            const isHorsesTable = table.closest('#horses') !== null;
            const isDamsTable = table.closest('#dams') !== null;
            const isauctioned_horses_table = table.closest('#auctioned-horses') !== null;

            const columnIndices = {
                group1: [],
                group2: [],
                group3: [],
                group4: []
            };

            headers.forEach((header, index) => {
                const columnName = header.getAttribute('data-column');
                if (isHorsesTable) {
                    if (group1Columns.includes(columnName)) columnIndices.group1.push(index);
                    if (group2Columns.includes(columnName)) columnIndices.group2.push(index);
                    if (group3Columns.includes(columnName)) columnIndices.group3.push(index);
                } else if (isDamsTable) {
                    if (group1Columns_dams.includes(columnName)) columnIndices.group1.push(index);
                    if (group2Columns_dams.includes(columnName)) columnIndices.group2.push(index);
                    if (group3Columns_dams.includes(columnName)) columnIndices.group3.push(index);
                    if (group4Columns_dams.includes(columnName)) columnIndices.group4.push(index);
                } else if (isauctioned_horses_table){
                    if (group1Columns_auctioned_horses.includes(columnName)) columnIndices.group1.push(index);
                }
            });

            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                cells.forEach(cell => {
                    cell.classList.remove('group-1-highlight', 'group-2-highlight', 'group-3-highlight', 'group-4-highlight');
                    cell.style.boxShadow = '';
                });

                columnIndices.group1.forEach(i => {
                    if (cells[i]) cells[i].classList.add('group-1-highlight');
                });
                columnIndices.group2.forEach(i => {
                    if (cells[i]) cells[i].classList.add('group-2-highlight');
                });
                columnIndices.group3.forEach(i => {
                    if (cells[i]) cells[i].classList.add('group-3-highlight');
                });
                columnIndices.group4.forEach(i => {
                    if (cells[i]) cells[i].classList.add('group-4-highlight');
                });
            });
        });
    }

    function attachSortableHandlers(table) {
        const headers = getColumnHeaders(table);

        headers.forEach((header, index) => {
            const columnName = header.getAttribute('data-column');
            if (sortableColumns.includes(columnName)) {
                header.classList.add('sortable');
                header.addEventListener('click', () => {
                    const tbody = table.querySelector('tbody');
                    const rows = Array.from(tbody.querySelectorAll('tr'));
                    const currentSort = header.classList.contains('sort-asc') ? 'desc' : 'asc';

                    headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
                    header.classList.add(`sort-${currentSort}`);

                    const columnType = columnConfig[columnName].type;

                    rows.sort((a, b) => {
                        const aVal = parseValue(a.children[index].textContent.trim(), columnType);
                        const bVal = parseValue(b.children[index].textContent.trim(), columnType);
                        return compareValues(aVal, bVal, columnType, currentSort);
                    });

                    rows.forEach(row => tbody.appendChild(row));

                    applyGradientHighlighting();
                    applyColumnHighlighting();
                });
            }
        });
    }

    tables.forEach(table => {
        attachSortableHandlers(table);
    });

    applyGradientHighlighting();
    applyColumnHighlighting();
});