//
//  STAvatarView.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

@protocol STAvatarViewDelegate;
@interface STAvatarView : UIView {
    UIView *highlightView;
}

@property(nonatomic,retain) NSURL *imageURL;
@property(nonatomic,retain,readonly) UIImageView *imageView;
@property(nonatomic,retain,readonly) UIView *backgroundView;
@property(nonatomic,assign) id <STAvatarViewDelegate> delegate;

- (void)setDefault;

@end

@protocol STAvatarViewDelegate
- (void)stAvatarViewTapped:(STAvatarView*)view;
@end