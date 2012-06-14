//
//  UserStampView.h
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import <UIKit/UIKit.h>


@interface UserStampView : UIControl {
    float r,g,b;
    float r1, g1, b1;
}

@property(nonatomic,assign) STStampImageSize size;

- (void)setupWithUser:(id<STUser>)user;
- (void)setupWithColors:(NSArray*)colors;
- (NSArray*)colors;

@end
