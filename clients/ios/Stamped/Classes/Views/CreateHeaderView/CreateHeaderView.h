//
//  CreateHeaderView.h
//  Stamped
//
//  Created by Devin Doty on 6/13/12.
//
//

#import <UIKit/UIKit.h>

@interface CreateHeaderView : UIControl {
    UILabel *_detailTitleLabel;
    UIImageView *_imageView;
}

- (void)setupWithItem:(id)item;

@property (nonatomic, readonly, assign) UILabel* titleLabel;

@end
