//
//  GifturePhotoViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/25/12.
//
//

#import <UIKit/UIKit.h>

@interface STPhotoViewController : UIViewController {
    NSURL *_URL;
}
- (id)initWithURL:(NSURL*)aURL;
@property(nonatomic,copy) NSString *photoTitle;

@end
