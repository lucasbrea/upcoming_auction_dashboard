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
                const allowedFilters = ['Haras','Horse', 'Name', 'Sire', 'Dam', 'Href', 'Sex', 'Criador', 'Year']; // Only allow these filters
                
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
        'TPBRS': { type: 'percentage' },
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
        'Auction Order':{type: 'number'},

       
    };

    const gradientColumns = [
        'G1 Wins',
        'G1 Wins / Races',
        'G1 Wnrs / Born (Historic)',
        'G1 Wnrs / Born (Last 2 yrs)',
        'Historic Run Share at 4yo',
        'Inbreeding Coef.',
        'Number of Top 100 BSNs / Number of 3&4yo offsprings',
        'PB',
        'PBRS',
        'PR',
        'PRS',
        'PS',
        'TPBRS'

      ];
    const sortableColumns = Object.keys(columnConfig);
    const tables = document.querySelectorAll('.table');

    const group1Columns = [
        
        'Ranking Gen23',
        'Horse',
        'Sire',
         'Dam',
         'Haras',
         'Sex',
         'Birth Month',
         'Birth Date',

                        ];
    const group2Columns = [
        'PRS',
        'PR',
        'PS',
    ];
    const group3Columns = [
        'Sire PS',
        'Dam\'s Age and Racing Career',
        'Dam\'s Offsprings Performance',
        'Dam\'s Family (Parents & Siblings)',
    ];
    const group4Columns = [
        'STK Races /Races',
        'STK Wins 2-5yo/#2-5yo',
        'Recent G1 Wnrs/Born',
    ];
    const group5Columns = [
        'Age',
        'Top BSNs',
        'Raced Stk? Won G-Stk? Won-G1?',
        '#Offs Ran',
        'Offs Top BSNs',
        'Offs Wnrs before 3yo(non-ALT)',
        'Offs Stk Wnrs',
        'CEI per offs(**)',
        'Dam\'s Siblings(GS) Stk wins',
    ];
    const group6Columns = [
        'PRS Value (2.200 USDB per Bps)',
    ];
    const group7columns = [
        'Start',
        'End',
        'Lote',
        'Href'
    ];
    const group1Columns_dams = [
        'Ranking',
        'Name',
        'Sire',
        'Dam',
        'Haras',
    ];
    const group2Columns_dams = [
        'Age and Racing Career',
        'Offsprings\' Quality',
        'Siblings\' quality',
        'Parents Career',
    ];
    const group3Columns_dams = [
        'Age',
        'Top 3 BSN\'s',
        'Raced Stk? Won G-Stk?',
        '#Offs Ran',
        'Dam\'s Foals Top 3 BSN',
        'Foals wnrs before 3yo(non-ALT)',  
        'Foals Stk Rnrs',
        'Foals Stk Wnrs',
        'Siblings total G-stk runs',
        'Siblings total G-stk wins',
    ];
    const group4Columns_dams = [
        '#Offs Ran / #Running age',
        '#Services',
        '#Births',
        'Date last service',
    ];
    const group5Columns_dams = [
        'Total Races',
        'Total Wins',
        'Stk Races',
        'Stk Wins',
        'G1 Placed',
        'G1 Wins',
        'CEI',

    ]
    const group6Columns_dams = [
        'Lote',
        'Start',
        'End',
        'Href'
    ];
    const groupInbreedingDams = ['Inbreeding Coef.']
    const groupSelectionDams = ['TPBRS','PBRS', 'PRS', 'PR', 'PS', 'PB']

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
            const tabPane = table.closest('.tab-pane');
            const tabId = tabPane?.id;

            const maxValues = 
                  tabId === 'horses' ? horsesMaxValues :
                  tabId === 'dams' ? damsMaxValues :
                  tabId === 'auctioned-horses' ? auctionedHorsesMaxValues :
                  tabId === 'test' ? testMaxValues :
                  {};

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

    function getLastColumnIndex(columns, headers) {
        for (let i = headers.length - 1; i >= 0; i--) {
            const columnName = headers[i].getAttribute('data-column');
            if (columns.includes(columnName)) return i;
        }
        return -1;
    }

    function applyColumnHighlighting() {
        tables.forEach(table => {
            const headers = getColumnHeaders(table);
            const rows = table.querySelectorAll('tbody tr');
            const tabPane = table.closest('.tab-pane');
            const isHorsesTable = tabPane?.id === 'horses';
            const isDamsTable = tabPane?.id === 'dams';
            const isauctioned_horses_table = tabPane?.id === 'auctioned-horses';

            const columnIndices = {
                group1: [],
                group2: [],
                group3: [],
                group4: [],
                group5: [],
                group6: [],
                group7:[],
                group1dams: [],
                group2dams: [],
                group3dams: [],
                group4dams: [],
                group5dams: [],
                group6dams: [],
    
            };

            headers.forEach((header, index) => {
                const columnName = header.getAttribute('data-column') || header.textContent.trim();
                if (isHorsesTable) {
                    if (group1Columns.includes(columnName)) columnIndices.group1.push(index);
                    if (group2Columns.includes(columnName)) columnIndices.group2.push(index);
                    if (group3Columns.includes(columnName)) columnIndices.group3.push(index);
                    if (group4Columns.includes(columnName)) columnIndices.group4.push(index);
                    if (group5Columns.includes(columnName)) columnIndices.group5.push(index);
                    if (group6Columns.includes(columnName)) columnIndices.group6.push(index);
                    if (group1Columns.includes(columnName)) header.classList.add('group-basic');
                    if (group2Columns.includes(columnName)) header.classList.add('group-selection-horses');
                    if (group3Columns.includes(columnName)) header.classList.add('group-ps');
                    if (group4Columns.includes(columnName)) header.classList.add('group-sire-ps');
                    if (group5Columns.includes(columnName)) header.classList.add('group-dam-ps');
                    if (group6Columns.includes(columnName)) header.classList.add('group-internal-value');
                    if (group7columns.includes(columnName)) header.classList.add('group-auction');
                } else if (isDamsTable) {
                    if (group1Columns_dams.includes(columnName)) columnIndices.group1dams.push(index);
                    if (group2Columns_dams.includes(columnName)) columnIndices.group2dams.push(index);
                    if (group3Columns_dams.includes(columnName)) columnIndices.group3dams.push(index);
                    if (group4Columns_dams.includes(columnName)) columnIndices.group4dams.push(index);
                    if(group5Columns_dams.includes(columnName)) columnIndices.group5dams.push(index);
                    if (group1Columns_dams.includes(columnName)) header.classList.add('group-basic-dams');
                    if (groupSelectionDams.includes(columnName)) header.classList.add('group-basic-dams');
                    if (groupInbreedingDams.includes(columnName)) header.classList.add('group-inbreeding-dams');
                    if (group2Columns_dams.includes(columnName)) header.classList.add('group-ps-dam');
                    if (group3Columns_dams.includes(columnName)) header.classList.add('main-characteristics-dams');
                    if (group4Columns_dams.includes(columnName)) header.classList.add('group-pb-dam');
                    if (group5Columns_dams.includes(columnName)) header.classList.add('group-racing-dam');
                    if (group6Columns_dams.includes(columnName)) header.classList.add('group-auction');
                } else if (isauctioned_horses_table){
                    if (group1Columns_auctioned_horses.includes(columnName)) columnIndices.group1.push(index);
                }
            });

            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                cells.forEach(cell => {
                    cell.classList.remove('group-1-highlight', 'group-2-highlight', 'group-3-highlight', 'group-4-highlight', 'group-5-highlight', 'group-6-highlight');
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
                columnIndices.group5.forEach(i => {
                    if (cells[i]) cells[i].classList.add('group-5-highlight');
                });
                columnIndices.group6.forEach(i => {
                    if (cells[i]) cells[i].classList.add('group-6-highlight');
                });
                columnIndices.group1dams.forEach(i => {
                    if (cells[i]) cells[i].classList.add('group-1dams-highlight');
                } );    
                columnIndices.group2dams.forEach(i => {
                    if (cells[i]) cells[i].classList.add('group-2dams-highlight');
                });
                columnIndices.group3dams.forEach(i => {
                    if (cells[i]) cells[i].classList.add('group-3dams-highlight');
                });
                columnIndices.group4dams.forEach(i => {
                    if (cells[i]) cells[i].classList.add('group-4dams-highlight');
                });
                columnIndices.group5dams.forEach(i => {
                    if (cells[i]) cells[i].classList.add('group-5dams-highlight');
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
