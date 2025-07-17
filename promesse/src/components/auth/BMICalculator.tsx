import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Calculator } from 'lucide-react';

export interface BMICalculatorProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (bmi: number, height: string, weight: string) => void;
}

export const BMICalculator: React.FC<BMICalculatorProps> = ({ isOpen, onClose, onSave }) => {
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [heightUnit, setHeightUnit] = useState<'cm' | 'ft'>('cm');
  const [weightUnit, setWeightUnit] = useState<'kg' | 'lbs'>('kg');
  const [feet, setFeet] = useState('');
  const [inches, setInches] = useState('');

  const calculateBMI = () => {
    let heightInMeters = 0;
    let weightInKg = 0;

    if (heightUnit === 'cm') {
      heightInMeters = parseFloat(height) / 100;
    } else {
      const totalInches = parseFloat(feet) * 12 + parseFloat(inches);
      heightInMeters = totalInches * 0.0254;
    }

    if (weightUnit === 'kg') {
      weightInKg = parseFloat(weight);
    } else {
      weightInKg = parseFloat(weight) * 0.453592;
    }

    const bmi = weightInKg / (heightInMeters * heightInMeters);
    const heightStr = heightUnit === 'cm' ? `${height}cm` : `${feet}'${inches}"`;
    const weightStr = `${weight}${weightUnit}`;

    onSave(Math.round(bmi * 10) / 10, heightStr, weightStr);
    onClose();
  };

  const isValid = () => {
    if (heightUnit === 'cm') {
      return height && parseFloat(height) > 0 && weight && parseFloat(weight) > 0;
    } else {
      return feet && inches && parseFloat(feet) > 0 && parseFloat(inches) >= 0 && weight && parseFloat(weight) > 0;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="sm:max-w-[400px] bg-gray-950">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Calculator className="h-5 w-5" />
            BMI Calculator
          </DialogTitle>
          <DialogDescription>
            Calculate your Body Mass Index automatically
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>Height</Label>
            <div className="flex gap-2">
              <Select value={heightUnit} onValueChange={(value: 'cm' | 'ft') => setHeightUnit(value)}>
                <SelectTrigger className="w-20 bg-gray-700">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cm">cm</SelectItem>
                  <SelectItem value="ft">ft</SelectItem>
                </SelectContent>
              </Select>
              {heightUnit === 'cm' ? (
                <Input placeholder="170" value={height} onChange={(e) => setHeight(e.target.value)} className="bg-gray-700" type="number" />
              ) : (
                <div className="flex gap-1 flex-1">
                  <Input placeholder="5" value={feet} onChange={(e) => setFeet(e.target.value)} className="bg-gray-700" type="number" />
                  <span className="self-center text-sm">ft</span>
                  <Input placeholder="8" value={inches} onChange={(e) => setInches(e.target.value)} className="bg-gray-700" type="number" />
                  <span className="self-center text-sm">in</span>
                </div>
              )}
            </div>
          </div>
          <div className="grid gap-2">
            <Label>Weight</Label>
            <div className="flex gap-2">
              <Select value={weightUnit} onValueChange={(value: 'kg' | 'lbs') => setWeightUnit(value)}>
                <SelectTrigger className="w-20 bg-gray-700">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="kg">kg</SelectItem>
                  <SelectItem value="lbs">lbs</SelectItem>
                </SelectContent>
              </Select>
              <Input placeholder={weightUnit === 'kg' ? '70' : '154'} value={weight} onChange={(e) => setWeight(e.target.value)} className="bg-gray-700 flex-1" type="number" />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="button" onClick={calculateBMI} disabled={!isValid()}>
            Calculate BMI
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
