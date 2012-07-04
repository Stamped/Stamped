//
//  STMusicPickerViewController.h
//  Stamped
//
//  Created by Devin Doty on 6/19/12.
//
//

#import <UIKit/UIKit.h>
#import <MediaPlayer/MediaPlayer.h>

typedef enum {
    STMusicPickerQueryTypeSong = 0,
    STMusicPickerQueryTypeAlbum,
    STMusicPickerQueryTypeArtist,
} STMusicPickerQueryType;

@protocol STMusicPickerViewControllerDelegate;
@interface STMusicPickerViewController : UITableViewController

- (id)initWithQueryType:(STMusicPickerQueryType)type;

@property(nonatomic,assign) id <STMusicPickerViewControllerDelegate> delegate;

@end
@protocol STMusicPickerViewControllerDelegate
- (void)stMusicPickerController:(STMusicPickerViewController*)controller didPickMediaItem:(MPMediaItem*)item;
@end
