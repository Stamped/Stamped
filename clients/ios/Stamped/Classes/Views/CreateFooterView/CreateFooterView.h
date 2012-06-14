//
//  CreateFooterView.h
//  Stamped
//
//  Created by Devin Doty on 6/13/12.
//
//

#import <UIKit/UIKit.h>

@protocol CreateFooterViewDelegate;
@interface CreateFooterView : UIView

@property(nonatomic,assign) id <CreateFooterViewDelegate> delegate;

@end
@protocol CreateFooterViewDelegate
- (void)createFooterView:(CreateFooterView*)view twitterSelected:(UIButton*)button;
- (void)createFooterView:(CreateFooterView*)view facebookSelected:(UIButton*)button;
- (void)createFooterView:(CreateFooterView*)view stampIt:(UIButton*)button;
@end
