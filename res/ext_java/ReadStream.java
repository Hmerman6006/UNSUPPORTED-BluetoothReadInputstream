package org.kivy.android;

import java.io.InputStream;
import java.io.BufferedReader;
import java.lang.Integer;
import java.lang.String;
import java.lang.StringBuilder;
import java.lang.Character;
import java.io.IOException;
import java.lang.System;
import java.io.InputStreamReader;

public class ReadStream {
    public static String readstream(InputStream stream) throws IOException {
        BufferedReader buffer = new BufferedReader(
                 new InputStreamReader(stream));
        int c = 0;
        StringBuilder sb = new StringBuilder();
        while((c = buffer.read()) != -1) {
            if (c == 10 || c == 13) {
                break;
            }
            sb.append((char) c);
        }
        return sb.toString();
    }
}