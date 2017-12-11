package com.thomasdeanwhite.gui.runtypes.interaction;

import com.google.gson.Gson;
import com.thomasdeanwhite.gui.App;
import com.thomasdeanwhite.gui.Properties;
import com.thomasdeanwhite.gui.output.StateComparator;
import com.thomasdeanwhite.gui.sampler.MouseEvent;

import java.io.*;
import java.util.*;

/**
 * Created by thoma on 21/06/2017.
 */
public class DeepLearningInteraction extends UserInteraction {
    private long minTime = Long.MAX_VALUE;

    private float mouseSpeed = 5f;

    private static final float CLICK_THRESHOLD = 0.25f;

    protected static float RANDOM_PROBABILITY = 0.005f;

    protected static float JITTER = 0.0001f;

    protected Event lastEvent = Event.NONE;
    protected Event secondLastEvent = lastEvent;

    private int iteration = 0;

    protected Event nextEvent;

    private Process pythonProcess;
    private BufferedWriter pythonWriter;

    private boolean modelFound = false;

    Gson gson;

    @Override
    public void load() throws IOException {
        super.load();

        App.out.println("- Looking for jar file in: " + System.getProperty("user.dir"));

        lastState = State.ORIGIN;
        states = new HashMap<>();

        gson = new Gson();

        lastState = captureState(Event.NONE);

        //TODO: Load any database info from previous runs
    }

    private boolean debugHeader = true;

    @Override
    public Event interact(long timePassed) {

        Event e;

        if (rawEvents.size() == 0) {
            return Event.NONE;
        }

        if (Math.random() <= RANDOM_PROBABILITY || lastEvent.equals(Event.NONE)) {
            int eventIndex = 1 + (int) Math.round(Math.random() * (rawEvents.size()-2));
            e = rawEvents.get(eventIndex);
            nextEvent = e;
            lastEvent = rawEvents.get(eventIndex-1);
        } else {
            double[] img = lastState.getImage();

            String input = "";

            for (double d : img)
                input += d + " ";


            String mouseInfo = lastEvent.toCsv()
                    .replace(",", " ");

            input += mouseInfo;

            try {
                if (pythonProcess == null) {
                    String pythonCommand = "%s";// + input;
                    Process process;

                    String pathToPythonScript = System.getProperty("user.dir") + "/nuimimic.jar";

                    try {


                        ProcessBuilder builder = new ProcessBuilder(String.format(pythonCommand, "python3"), pathToPythonScript);
                        builder.redirectErrorStream(true);
                        builder.directory(new File(System.getProperty("user.dir") + "/NuiMimic/data"));
                        process = builder.start();
                    } catch (IOException e2){
                        ProcessBuilder builder = new ProcessBuilder(String.format(pythonCommand, "python"), pathToPythonScript);
                        builder.redirectErrorStream(true);
                        builder.directory(new File(System.getProperty("user.dir") + "/NuiMimic/data"));
                        process = builder.start();
                    }
                    pythonProcess = process;

                    pythonWriter = new BufferedWriter(
                            new OutputStreamWriter(pythonProcess.getOutputStream())
                    );



                    new Thread(() -> {
                        BufferedReader br = new BufferedReader(new InputStreamReader(pythonProcess.getInputStream()));
                        BufferedReader be = new BufferedReader(new InputStreamReader(pythonProcess.getErrorStream()));

                        String line;

                        try {
                            while ((line = br.readLine()) != null && line.trim().length() > 0) {
                                if (!line.toLowerCase().contains("dl-result")){
                                    continue;
                                }
                                DeepLearningInteraction.this.processLine(line.substring(line.indexOf(" ")+1));
                            }

                            while ((line = be.readLine()) != null) {
                                App.out.println(line);
                            }
                        } catch (IOException e1) {
                            e1.printStackTrace();
                        }

                        try {
                            pythonProcess.waitFor();
                        } catch (InterruptedException e1) {
                            e1.printStackTrace();
                        }
                        pythonProcess.destroy();
                        pythonProcess = null;
                    }).start();
                }

                pythonWriter.write(input + "\n");
                //pythonProcess.getOutputStream().flush();

            } catch (IOException e1) {
                e1.printStackTrace();
                nextEvent = Event.NONE;
            }

        }

        return nextEvent == null ? Event.NONE : nextEvent;
    }

    public void processLine (String line){

//        if (Properties.SHOW_OUTPUT) {
//            App.out.println("\rlem: " + lastEvent.toString() + " disp: " + line);
//        }

        if (line.contains("model loaded")){
            modelFound = true;
            App.out.println("- DNN Loaded successfully!");
            return;
        }

        if (!modelFound){
            throw new ModelNotFoundException("Model could not be found in ./NuiMimic/data");
        }


        //output: x y lmm rmm
        //x y lmm rmm
        String[] eles = line.split(" ");
        float lmm = Float.parseFloat(eles[2]);
        float rmm = Float.parseFloat(eles[3]);

        MouseEvent me = MouseEvent.NONE;

//        if (lastEvent.getEvent().equals(MouseEvent.LEFT_DOWN) || lastEvent.getEvent().equals(MouseEvent.DRAGGED)){
//            me = MouseEvent.DRAGGED;
//        }


        if (lmm > rmm && lmm > CLICK_THRESHOLD) {
            me = MouseEvent.LEFT_DOWN;
        } else if (rmm > lmm && rmm > CLICK_THRESHOLD) {
            me = MouseEvent.RIGHT_CLICK;
        } else if (lmm < rmm && lmm < CLICK_THRESHOLD) {
            me = MouseEvent.LEFT_UP;
        } else if (rmm < lmm && rmm < CLICK_THRESHOLD) {
            me = MouseEvent.RIGHT_UP;
        }

//        int diffx = (int) (Float.parseFloat(eles[0]) * Event.bounds.getWidth());
//        int diffy = (int) (Float.parseFloat(eles[1]) * Event.bounds.getHeight());
//
//        float mag = (float) Math.sqrt(diffx * diffx + diffy * diffy);
//
//        diffx = (int)(mouseSpeed * diffx / mag);
//        diffy = (int)(mouseSpeed * diffy / mag);
//
//        int mx = (int)Math.max(Math.min(Event.bounds.getWidth(), lastEvent.getMouseX() + diffx), 0);
//        int my = (int)Math.max(Math.min(Event.bounds.getHeight(), lastEvent.getMouseY() + diffy), 0);

        nextEvent = new Event(me,
                0,
                0,
                System.currentTimeMillis(),
                iteration);
    }

    @Override
    public void postInteraction(Event e) {
        //super.postInteraction(e);

        State state = captureState(e);

        lastState = state;

        secondLastEvent = lastEvent;

        lastEvent = e;

        iteration++;

    }

    public State captureState(Event e) {
        double[] newImage = StateComparator.screenshotState(e.getMouseX(), e.getMouseY());

        int stateNumber = states.size();

        State state = new State(stateNumber, newImage, lastState.getStateNumber());

        states.put(stateNumber, state);
        StateComparator.captureState(state.getImage(), state.getStateNumber());

        return state;
    }
}