import React from 'react';
import { Button } from '@/components/ui/button';
import { Trash2 } from 'lucide-react';

interface BulkOperationsProps {
  selectedItems: number[];
  onBulkDelete: () => void;
}

const BulkOperations: React.FC<BulkOperationsProps> = ({ selectedItems, onBulkDelete }) => {
  if (selectedItems.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-4">
      <p>{selectedItems.length} items selected</p>
      <Button variant="destructive" onClick={onBulkDelete}>
        <Trash2 className="mr-2 h-4 w-4" />
        Delete Selected
      </Button>
    </div>
  );
};

export default BulkOperations;
