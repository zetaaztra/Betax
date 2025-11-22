import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { X, HelpCircle } from "lucide-react";

interface TileHelpModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description: string;
}

export function TileHelpModal({ open, onClose, title, description }: TileHelpModalProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]" data-testid="modal-tile-help">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              <HelpCircle className="h-5 w-5 text-primary" />
            </div>
            <DialogTitle className="text-lg">{title}</DialogTitle>
          </div>
          <DialogDescription className="text-left pt-4">
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <div className="text-foreground/90 leading-relaxed whitespace-pre-line">
                {description}
              </div>
            </div>
          </DialogDescription>
        </DialogHeader>
        <div className="flex justify-end mt-4">
          <Button onClick={onClose} variant="outline" data-testid="button-close-help">
            <X className="h-4 w-4 mr-2" />
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
