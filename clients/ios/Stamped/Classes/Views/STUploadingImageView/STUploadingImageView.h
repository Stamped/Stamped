//
//  STUploadingImageView.h
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import <UIKit/UIKit.h>

@protocol STUploadingImageViewDelegate;
@interface STUploadingImageView : UIImageView
@property(nonatomic,assign) UIButton *deleteButton;
@property(nonatomic,retain) UIActivityIndicatorView *activiyView;
@property(nonatomic,assign) BOOL uploading;
@property(nonatomic,assign) id <STUploadingImageViewDelegate> delegate;
@end

@protocol STUploadingImageViewDelegate
- (void)sTUploadingImageViewTapped:(STUploadingImageView*)view;
@end