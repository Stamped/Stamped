//
//  CreateHeaderView.h
//  Stamped
//
//  Created by Devin Doty on 6/13/12.
//
//

#import <UIKit/UIKit.h>

@interface CreateHeaderView : UIControl {
    UILabel *_titleLabel;
    UILabel *_detailTitleLabel;
    UIImageView *_imageView;
}

- (void)setupWithItem:(id)item;

@end
