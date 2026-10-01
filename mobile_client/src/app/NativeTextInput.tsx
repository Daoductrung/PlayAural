import {
  forwardRef,
  useCallback,
  useLayoutEffect,
  useRef,
  type ForwardedRef,
} from "react";
import {
  Platform,
  TextInput as ReactNativeTextInput,
  type TextInputProps,
} from "react-native";

export type NativeTextInputProps = Omit<TextInputProps, "defaultValue" | "onChangeText" | "value"> & {
  onChangeText?: TextInputProps["onChangeText"];
  value: string;
};

function assignRef<T>(ref: ForwardedRef<T>, value: T | null): void {
  if (typeof ref === "function") {
    ref(value);
    return;
  }
  if (ref) {
    ref.current = value;
  }
}

/**
 * Keeps Android editing native-owned while retaining React state as the
 * application model. Controlled React Native text fields cause affected
 * TalkBack releases to report every keystroke as a whole-value replacement.
 * Native edits update the model without writing the same value back; genuine
 * application changes (clear, restore, or a new server value) are applied
 * imperatively. Other platforms retain normal controlled-input behavior.
 */
export const NativeTextInput = forwardRef<ReactNativeTextInput, NativeTextInputProps>(
  function NativeTextInput({ onChangeText, value, ...props }, forwardedRef) {
    const inputRef = useRef<ReactNativeTextInput | null>(null);
    const initialAndroidValueRef = useRef(value);
    const nativeAndroidValueRef = useRef(value);

    const setInputRef = useCallback((node: ReactNativeTextInput | null) => {
      inputRef.current = node;
      assignRef(forwardedRef, node);
    }, [forwardedRef]);

    const handleChangeText = useCallback((text: string) => {
      if (Platform.OS === "android") {
        nativeAndroidValueRef.current = text;
      }
      onChangeText?.(text);
    }, [onChangeText]);

    useLayoutEffect(() => {
      if (Platform.OS !== "android" || nativeAndroidValueRef.current === value) {
        return;
      }
      const input = inputRef.current;
      if (!input) {
        return;
      }
      nativeAndroidValueRef.current = value;
      input.setNativeProps({ text: value });
    }, [value]);

    const textValueProps = Platform.OS === "android"
      ? { defaultValue: initialAndroidValueRef.current }
      : { value };

    return (
      <ReactNativeTextInput
        {...props}
        {...textValueProps}
        onChangeText={handleChangeText}
        ref={setInputRef}
      />
    );
  },
);
