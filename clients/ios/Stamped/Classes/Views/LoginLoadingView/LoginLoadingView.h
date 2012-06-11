//
//  LoginLoadingView.h
//  Stamped
//
//  Created by Devin Doty on 6/7/12.
//
//

#import <UIKit/UIKit.h>

@interface LoginLoadingView : UIView {
    UIActivityIndicatorView *_activityView;
}
@property(nonatomic,retain) UILabel *titleLabel;
@end