//
//  UserStampView.h
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import <UIKit/UIKit.h>


@interface UserStampView : UIView {
    UIColor *_color1;
    UIColor *_color2;
}

@property(nonatomic,assign) STStampImageSize size;
@property(nonatomic,assign,getter = isHighlighted) BOOL highlighted;

- (void)setupWithUser:(id<STUser>)user;
- (void)setupWithColors:(NSArray*)colors;

@end
