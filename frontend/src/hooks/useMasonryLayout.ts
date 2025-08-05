import { useEffect, useRef, useCallback } from 'react';

interface MasonryOptions {
  gap: number;
  minColumnWidth: number;
}

export const useMasonryLayout = (items: any[], options: MasonryOptions) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const itemsRef = useRef<HTMLDivElement[]>([]);

  const calculateLayout = useCallback(() => {
    const container = containerRef.current;
    if (!container || items.length === 0) return;

    // Debug container information
    const containerWidth = container.offsetWidth || container.clientWidth;
    const parentWidth = container.parentElement?.offsetWidth || 0;
    const grandParentWidth = container.parentElement?.parentElement?.offsetWidth || 0;
    
    // Get container's computed style to check for padding
    const containerStyle = window.getComputedStyle(container);
    const paddingLeft = parseFloat(containerStyle.paddingLeft);
    const paddingRight = parseFloat(containerStyle.paddingRight);
    const availableWidth = containerWidth - paddingLeft - paddingRight;
    
    const { gap, minColumnWidth } = options;
    
    console.log('Container hierarchy widths:', {
      container: containerWidth,
      availableWidth: availableWidth,
      paddingLeft: paddingLeft,
      paddingRight: paddingRight,
      parent: parentWidth,
      grandParent: grandParentWidth,
      containerClass: container.className,
      parentClass: container.parentElement?.className,
      grandParentClass: container.parentElement?.parentElement?.className
    });
    
    if (availableWidth === 0 || availableWidth < 100) {
      // Container not ready, try again later
      console.log('Container not ready, available width:', availableWidth);
      setTimeout(() => calculateLayout(), 100);
      return;
    }
    
    // Responsive column count based on window width for more reliable detection
    const windowWidth = window.innerWidth;
    let columnCount: number;
    
    if (windowWidth >= 2200) {
      columnCount = 6;
    } else if (windowWidth >= 1800) {
      columnCount = 5;
    } else if (windowWidth >= 1400) {
      columnCount = 4;
    } else if (windowWidth >= 1200) {
      columnCount = 3;
    } else if (windowWidth >= 768) {
      columnCount = 2;
    } else {
      columnCount = 1;
    }
    
    // Temporarily force multiple columns for debugging
    if (availableWidth > 800 && columnCount === 1) {
      columnCount = 3; // Force at least 3 columns for wide containers
      console.log('Forced column count to 3 for debugging');
    }
    
    // Ensure we don't exceed what the container can actually fit
    const maxPossibleColumns = Math.floor((availableWidth + gap) / (minColumnWidth + gap));
    const originalColumnCount = columnCount;
    columnCount = Math.min(columnCount, Math.max(1, maxPossibleColumns));
    
    console.log('Original column count:', originalColumnCount, 'Max possible:', maxPossibleColumns, 'Final:', columnCount);
    
    const columnWidth = (availableWidth - gap * (columnCount - 1)) / columnCount;
    const columnHeights = new Array(columnCount).fill(0);
    
    console.log('Window width:', windowWidth, 'Container width:', containerWidth, 'Available width:', availableWidth, 'Columns:', columnCount, 'Column width:', columnWidth);

    // First pass: set widths and reset positions
    itemsRef.current.forEach((item, index) => {
      if (!item) return;
      item.style.width = `${columnWidth}px`;
      item.style.transition = 'none';
      item.style.position = 'absolute';
    });

    // Force reflow to ensure width changes are applied
    void container.offsetHeight;

    // Second pass: calculate positions based on actual heights
    itemsRef.current.forEach((item, index) => {
      if (!item) return;

      // Get actual height after width is set
      const cardHeight = item.offsetHeight;
      
      // Find shortest column
      const shortestColumnIndex = columnHeights.indexOf(Math.min(...columnHeights));
      const x = paddingLeft + shortestColumnIndex * (columnWidth + gap);
      const y = columnHeights[shortestColumnIndex];

      // Position the card
      item.style.left = `${x}px`;
      item.style.top = `${y}px`;
      
      // Update column height
      columnHeights[shortestColumnIndex] += cardHeight + gap;
      
      console.log(`Card ${index}: Column ${shortestColumnIndex}, Position (${x}, ${y}), Height ${cardHeight}, Column heights:`, [...columnHeights]);
    });

    // Enable transitions after positioning
    requestAnimationFrame(() => {
      itemsRef.current.forEach((item) => {
        if (item) {
          item.style.transition = 'all 0.3s ease';
        }
      });
    });

    // Set container height after all cards are positioned
    const maxHeight = Math.max(...columnHeights);
    container.style.height = `${maxHeight}px`;
    console.log('Final container height:', maxHeight, 'Column heights:', columnHeights);
  }, [items, options]);

  const addItemRef = useCallback((element: HTMLDivElement | null, index: number) => {
    if (element) {
      itemsRef.current[index] = element;
    }
  }, []);

  useEffect(() => {
    const handleResize = () => {
      calculateLayout();
    };

    // Initial layout with multiple attempts to ensure container is ready
    const timer1 = setTimeout(calculateLayout, 50);
    const timer2 = setTimeout(calculateLayout, 200);
    const timer3 = setTimeout(calculateLayout, 500);

    // Listen for window resize
    window.addEventListener('resize', handleResize);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      window.removeEventListener('resize', handleResize);
    };
  }, [calculateLayout]);

  // Recalculate when items change
  useEffect(() => {
    const timer = setTimeout(calculateLayout, 50);
    return () => clearTimeout(timer);
  }, [items, calculateLayout]);

  return {
    containerRef,
    addItemRef,
    recalculateLayout: calculateLayout
  };
};