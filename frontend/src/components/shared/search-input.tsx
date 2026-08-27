"use client";

import { useEffect, useRef, useState } from "react";
import { Input } from "@/components/ui/input";
import { SearchIcon, XIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface SearchInputProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  className?: string;
  debounceMs?: number;
}

export function SearchInput({
  value: controlledValue,
  onChange,
  placeholder = "جستجو...",
  className,
  debounceMs = 300,
}: SearchInputProps) {
  const [local, setLocal] = useState(controlledValue ?? "");
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;
  const isFirst = useRef(true);
  const skipDebounce = useRef(false);

  useEffect(() => {
    if (controlledValue !== undefined && controlledValue !== local) {
      skipDebounce.current = true;
      setLocal(controlledValue);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [controlledValue]);

  useEffect(() => {
    if (isFirst.current) {
      isFirst.current = false;
      return;
    }
    if (skipDebounce.current) {
      skipDebounce.current = false;
      return;
    }
    const t = setTimeout(() => {
      onChangeRef.current?.(local);
    }, debounceMs);
    return () => clearTimeout(t);
  }, [local, debounceMs]);

  return (
    <div className={cn("relative", className)}>
      <SearchIcon className="absolute right-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
      <Input
        value={local}
        onChange={(e) => setLocal(e.target.value)}
        placeholder={placeholder}
        className="pe-9 ps-9"
        aria-label={placeholder}
      />
      {local && (
        <button
          type="button"
          onClick={() => {
            setLocal("");
            onChangeRef.current?.("");
          }}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          aria-label="پاک کردن جستجو"
        >
          <XIcon className="size-4" />
        </button>
      )}
    </div>
  );
}
