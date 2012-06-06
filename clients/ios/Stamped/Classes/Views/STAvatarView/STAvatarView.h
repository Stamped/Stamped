//
//  STAvatarView.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

@interface STAvatarView : UIView
@property(nonatomic,retain) NSURL *imageURL;
@property(nonatomic,retain,readonly) UIImageView *imageView;
@property(nonatomic,retain,readonly) UIView *backgroundView;
@end
