distances = [0,1,2,4,6,9,12,16,21,30];

[optimizer, metric] = imregconfig('monomodal');

file = fopen('aufgabe1_parameter.txt','w');
fprintf(file, 'orig\tmov\tdist\tdx\tdy\tMI\tMSD\n');
basename = '/home/student/Desktop/Bilder/Bild%d.jpg';
for i=1:1:10
    
    filename1 = sprintf(basename, i);
    original = imread(filename1);
    original_gray = rgb2gray(original);
    
    dim = size(original_gray);
    reference = imref2d(dim);

    for j=1:1:10
        basename1 = '/home/student/Desktop/Bilder/Bild%d.jpg';
        filename2 = sprintf(basename, j);
        
        moving = imread(filename2);
        moving_gray = rgb2gray(moving);

        T = imregtform(moving_gray, original_gray, 'translation', optimizer, metric);
        transformed = imwarp(moving_gray, T, 'OutputView', reference);

        dx = T.T(3,1);
        dy = T.T(3,2);

        f1 = figure;
        imshowpair(original_gray, transformed), title(sprintf('Bilder %d-%d - dx=%f, dy=%f', i,j, dx, dy));
        saveas(f1, sprintf('Bilder_%d_%d.png', i,j))
        close(f1);
        
        MI = mutualInfo(original_gray, transformed);
        MSD = sum((original_gray-transformed).^2, 'all')/(dim(1)*dim(2));
    
        
        d = distances(i) - distances(j);
        fprintf(file, sprintf('%d\t%d\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n',i,j,d, dx, dy, MI, MSD));
    end
    
end

fclose(file);
