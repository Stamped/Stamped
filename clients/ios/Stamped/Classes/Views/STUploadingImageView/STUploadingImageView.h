//
//  STUploadingImageView.h
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import <UIKit/UIKit.h>

@interface STUploadingImageView : UIImageView
@property(nonatomic,retain) UIActivityIndicatorView *activiyView;
@property(nonatomic,assign) BOOL uploading;
@end
