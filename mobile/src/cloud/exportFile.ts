import * as FileSystem from "expo-file-system";
import * as Sharing from "expo-sharing";

export async function exportAndShare(filename: string, mimeType: string, content: string): Promise<void> {
  const uri = `${FileSystem.cacheDirectory}${filename}`;
  await FileSystem.writeAsStringAsync(uri, content);
  if (await Sharing.isAvailableAsync()) {
    await Sharing.shareAsync(uri, { mimeType, dialogTitle: filename });
  } else {
    throw new Error("Sharing is not available on this device");
  }
}
